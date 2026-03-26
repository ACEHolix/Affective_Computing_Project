#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import pickle
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset


class RegionGraphDataset(Dataset):
    def __init__(self, data_dir: str):
        self.files = sorted(Path(data_dir).glob("*.pkl"))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        with open(self.files[idx], "rb") as f:
            return pickle.load(f)


def collate_fn(batch):
    return {
        "x_eeg": torch.from_numpy(np.stack([item["x_eeg"] for item in batch], axis=0)).float(),
        "adj_eeg": torch.from_numpy(np.stack([item["adj_eeg"] for item in batch], axis=0)).float(),
        "label": torch.tensor([item["label"] for item in batch], dtype=torch.long),
    }


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


class SimpleGraphConv(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)

    def forward(self, x, adj):
        return self.linear(torch.bmm(adj, x))


class RegionStaticGCN(nn.Module):
    def __init__(self, in_dim=5, hidden_dim=64, out_dim=5, dropout=0.3):
        super().__init__()
        self.input_proj = nn.Linear(in_dim, hidden_dim)
        self.gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.gcn2 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, x, adj):
        h = F.relu(self.input_proj(x))
        h = F.relu(self.gcn1(h, adj))
        h = F.relu(self.gcn2(h, adj))
        z = h.mean(dim=1)
        return self.classifier(z)


def run_one_epoch(model, loader, optimizer, criterion, device, train: bool):
    model.train() if train else model.eval()
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


def save_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="训练脑区拓扑静态 GCN 第二版。")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--num-classes", type=int, default=5)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = RegionGraphDataset(args.data_dir)
    if len(dataset) == 0:
        raise RuntimeError(f"未找到样本: {args.data_dir}")

    fit_indices, val_indices, test_indices = build_split_indices(dataset, args.val_ratio, args.seed)
    train_loader = DataLoader(Subset(dataset, fit_indices), batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(Subset(dataset, val_indices), batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(Subset(dataset, test_indices), batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn)

    model = RegionStaticGCN(hidden_dim=args.hidden_dim, out_dim=args.num_classes, dropout=args.dropout).to(device)
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
        train_loss, train_acc = run_one_epoch(model, train_loader, optimizer, criterion, device, train=True)
        val_loss, val_acc = run_one_epoch(model, val_loader, optimizer, criterion, device, train=False)
        rec = {"epoch": epoch, "train_loss": train_loss, "train_acc": train_acc, "val_loss": val_loss, "val_acc": val_acc}
        history.append(rec)
        print(f"epoch={epoch} train_loss={train_loss:.4f} train_acc={train_acc:.4f} val_loss={val_loss:.4f} val_acc={val_acc:.4f}")
        torch.save({"epoch": epoch, "model_state": model.state_dict()}, checkpoint_dir / "last.pt")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            torch.save({"epoch": epoch, "model_state": model.state_dict()}, checkpoint_dir / "best.pt")

    best_ckpt = torch.load(checkpoint_dir / "best.pt", map_location=device)
    model.load_state_dict(best_ckpt["model_state"])
    test_loss, test_acc = run_one_epoch(model, test_loader, optimizer, criterion, device, train=False)

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
        "best_epoch": best_epoch,
        "best_val_acc": best_val_acc,
        "test_loss": test_loss,
        "test_acc": test_acc,
    }
    split_info = {"train_indices": fit_indices, "val_indices": val_indices, "test_indices": test_indices}
    save_json(metrics_dir / "summary.json", summary)
    save_json(metrics_dir / "history.json", {"history": history})
    save_json(metrics_dir / "split_indices.json", split_info)


if __name__ == "__main__":
    main()
