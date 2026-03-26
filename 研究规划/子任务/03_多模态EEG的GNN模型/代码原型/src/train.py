from pathlib import Path
import torch
from torch.utils.data import DataLoader

from dataset import MultiModalGraphDataset
from model import MultiModalEEGGNN


def collate_fn(batch):
    return {
        "x_eeg": torch.stack([item["x_eeg"] for item in batch], dim=0),
        "x_phy": torch.stack([item["x_phy"] for item in batch], dim=0),
        "adj_eeg": torch.stack([item["adj_eeg"] for item in batch], dim=0),
        "adj_phy": torch.stack([item["adj_phy"] for item in batch], dim=0),
        "adj_cross": torch.stack([item["adj_cross"] for item in batch], dim=0),
        "label": torch.tensor([item["label"] for item in batch], dtype=torch.long),
    }


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0

    for batch in loader:
        x_eeg = batch["x_eeg"].to(device)
        x_phy = batch["x_phy"].to(device)
        adj_eeg = batch["adj_eeg"].to(device)
        adj_phy = batch["adj_phy"].to(device)
        adj_cross = batch["adj_cross"].to(device)
        y = batch["label"].to(device)

        pred = model(x_eeg, x_phy, adj_eeg, adj_phy, adj_cross)
        loss = criterion(pred, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / max(len(loader), 1)


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    data_dir = Path(__file__).resolve().parents[1] / "data"
    dataset = MultiModalGraphDataset(data_dir)
    if len(dataset) == 0:
        raise RuntimeError(f"未找到训练样本，请先生成或导出 .pt 文件: {data_dir}")
    loader = DataLoader(dataset, batch_size=16, shuffle=True, collate_fn=collate_fn)

    model = MultiModalEEGGNN(
        eeg_in_dim=5,
        phy_in_dim=4,
        hidden_dim=64,
        out_dim=3,
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = torch.nn.CrossEntropyLoss()

    for epoch in range(10):
        loss = train_one_epoch(model, loader, optimizer, criterion, device)
        print(f"epoch={epoch} loss={loss:.4f}")


if __name__ == "__main__":
    main()
