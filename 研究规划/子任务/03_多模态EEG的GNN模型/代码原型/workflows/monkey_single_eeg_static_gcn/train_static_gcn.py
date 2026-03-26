#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset


TASK_LABELS = {
    "5cls": None,
    "csr_vs_csp": (1, 2),
    "usr_vs_usp": (3, 4),
}


class SingleEEGGraphDataset(Dataset):
    def __init__(self, data_dir: str, task_name: str = "5cls"):
        self.task_name = task_name
        self.files = []
        for path in sorted(Path(data_dir).glob("*.pkl")):
            with open(path, "rb") as f:
                sample = pickle.load(f)
            label = int(sample["label"])
            if self._keep_label(label):
                self.files.append(path)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        with open(self.files[idx], "rb") as f:
            sample = pickle.load(f)
        sample["label"] = self._remap_label(int(sample["label"]))
        return sample

    def _keep_label(self, label: int) -> bool:
        target = TASK_LABELS[self.task_name]
        if target is None:
            return True
        return label in target

    def _remap_label(self, label: int) -> int:
        target = TASK_LABELS[self.task_name]
        if target is None:
            return label
        return 0 if label == target[0] else 1


def build_split_indices(dataset: Dataset, val_ratio: float, seed: int):
    train_indices = []
    test_indices = []
    for idx, path in enumerate(dataset.files):
        if "_test_" in path.name:
            test_indices.append(idx)
        else:
            train_indices.append(idx)

    rng = np.random.default_rng(seed)
    train_indices = np.array(train_indices, dtype=np.int64)
    rng.shuffle(train_indices)
    n_val = max(1, int(len(train_indices) * val_ratio))
    val_indices = train_indices[:n_val].tolist()
    fit_indices = train_indices[n_val:].tolist()
    if not fit_indices:
        fit_indices = val_indices[:]
    return fit_indices, val_indices, test_indices


def collate_fn(batch):
    return {
        "x_eeg": torch.from_numpy(np.stack([item["x_eeg"] for item in batch], axis=0)).float(),
        "adj_eeg": torch.from_numpy(np.stack([item["adj_eeg"] for item in batch], axis=0)).float(),
        "label": torch.tensor([item["label"] for item in batch], dtype=torch.long),
    }


class SimpleGraphConv(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)

    def forward(self, x, adj):
        return self.linear(torch.bmm(adj, x))


class EEGStaticGCN(nn.Module):
    def __init__(self, eeg_in_dim=5, hidden_dim=64, out_dim=5, dropout=0.3):
        super().__init__()
        self.input_proj = nn.Linear(eeg_in_dim, hidden_dim)
        self.gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.gcn2 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, x_eeg, adj_eeg):
        h = F.relu(self.input_proj(x_eeg))
        h = F.relu(self.gcn1(h, adj_eeg))
        h = F.relu(self.gcn2(h, adj_eeg))
        z = h.mean(dim=1)
        return self.classifier(z)


def run_one_epoch(model, loader, optimizer, criterion, device, train: bool):
    if train:
        model.train()
    else:
        model.eval()
    model.train()
    total_loss = 0.0
    total_correct = 0
    total = 0
    with torch.set_grad_enabled(train):
        for batch in loader:
            x = batch["x_eeg"].to(device)
            adj = batch["adj_eeg"].to(device)
            y = batch["label"].to(device)
            pred = model(x, adj)
            loss = criterion(pred, y)
            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            total_loss += loss.item()
            total_correct += (pred.argmax(dim=1) == y).sum().item()
            total += y.numel()
    return total_loss / max(len(loader), 1), total_correct / max(total, 1)


def evaluate(model, loader, criterion, device):
    return run_one_epoch(model, loader, None, criterion, device, train=False)


def train_one_epoch(model, loader, optimizer, criterion, device):
    return run_one_epoch(model, loader, optimizer, criterion, device, train=True)


def save_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="训练单模态 EEG 静态 GCN baseline。")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--num-classes", type=int, default=5)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--task", type=str, default="5cls", choices=list(TASK_LABELS.keys()))
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = SingleEEGGraphDataset(args.data_dir, task_name=args.task)
    if len(dataset) == 0:
        raise RuntimeError(f"未找到样本: {args.data_dir}")

    fit_indices, val_indices, test_indices = build_split_indices(dataset, args.val_ratio, args.seed)
    train_loader = DataLoader(Subset(dataset, fit_indices), batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(Subset(dataset, val_indices), batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(Subset(dataset, test_indices), batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn)

    model = EEGStaticGCN(hidden_dim=args.hidden_dim, out_dim=args.num_classes, dropout=args.dropout).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion = nn.CrossEntropyLoss()

    run_dir = Path(args.run_dir)
    checkpoint_dir = run_dir / "checkpoints"
    metrics_dir = run_dir / "metrics"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    history = []
    best_val_acc = -1.0
    best_epoch = -1

    for epoch in range(args.epochs):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
        }
        history.append(record)
        print(
            f"epoch={epoch} "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
        )
        torch.save({"epoch": epoch, "model_state": model.state_dict()}, checkpoint_dir / "last.pt")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            torch.save({"epoch": epoch, "model_state": model.state_dict()}, checkpoint_dir / "best.pt")

    best_ckpt = torch.load(checkpoint_dir / "best.pt", map_location=device)
    model.load_state_dict(best_ckpt["model_state"])
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)

    summary = {
        "run_name": run_dir.name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data_dir": str(Path(args.data_dir).resolve()),
        "device": str(device),
        "num_samples": len(dataset),
        "num_train": len(fit_indices),
        "num_val": len(val_indices),
        "num_test": len(test_indices),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "hidden_dim": args.hidden_dim,
        "num_classes": args.num_classes,
        "dropout": args.dropout,
        "learning_rate": args.learning_rate,
        "val_ratio": args.val_ratio,
        "seed": args.seed,
        "task": args.task,
        "best_epoch": best_epoch,
        "best_val_acc": best_val_acc,
        "test_loss": test_loss,
        "test_acc": test_acc,
    }
    split_info = {
        "train_indices": fit_indices,
        "val_indices": val_indices,
        "test_indices": test_indices,
    }

    save_json(metrics_dir / "history.json", {"history": history})
    save_json(metrics_dir / "summary.json", summary)
    save_json(metrics_dir / "split_indices.json", split_info)


if __name__ == "__main__":
    main()
