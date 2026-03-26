from pathlib import Path
import torch


def main():
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    sample = {
        "sample_id": "sub01_trial01_win01",
        "subject_id": "sub01",
        "trial_id": "trial01",
        "window_id": 1,
        "label": 0,
        "x_eeg": torch.randn(32, 5),
        "x_phy": torch.randn(3, 4),
        "adj_eeg": torch.eye(32),
        "adj_phy": torch.ones(3, 3),
        "adj_cross": torch.ones(35, 35),
    }

    torch.save(sample, out_dir / "sample_000.pt")
    print("dummy sample saved")


if __name__ == "__main__":
    main()
