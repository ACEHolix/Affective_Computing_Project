from pathlib import Path
import json


def main():
    root = Path(__file__).resolve().parents[1] / "data" / "raw"
    trial_dir = root / "sub01" / "trial01"
    trial_dir.mkdir(parents=True, exist_ok=True)

    for name in ["eeg.csv", "ecg.csv", "resp.csv", "eda.csv"]:
        (trial_dir / name).write_text("timestamp,value\n0,0.0\n", encoding="utf-8")

    with open(trial_dir / "label.json", "w", encoding="utf-8") as f:
        json.dump({"label": 0}, f, ensure_ascii=False, indent=2)

    print(f"raw dataset template created at: {root}")


if __name__ == "__main__":
    main()
