from pathlib import Path
import torch
from torch.utils.data import Dataset


class MultiModalGraphDataset(Dataset):
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.files = sorted(self.data_dir.glob("*.pt"))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        sample = torch.load(self.files[idx], map_location="cpu")
        return sample
