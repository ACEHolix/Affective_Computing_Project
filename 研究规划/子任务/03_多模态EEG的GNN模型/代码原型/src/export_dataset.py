from pathlib import Path
import json
import torch

from io_templates import iter_trial_records
from preprocess import build_sample, export_sample


def load_csv_placeholder(path: Path):
    """
    真实实现入口占位：
    这里后续替换成 pandas / numpy 读取逻辑。
    """
    return {
        "path": str(path),
        "exists": path.exists(),
    }


def load_label_placeholder(path: Path):
    """
    标签读取占位。
    后续替换成真实标签格式解析。
    """
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("label", 0)
        except Exception:
            return 0
    return 0


def build_raw_modalities(record):
    files = record["files"]
    return {
        "subject_id": record["subject_id"],
        "trial_id": record["trial_id"],
        "window_id": 0,
        "eeg": load_csv_placeholder(files["eeg"]) | {"n_channels": 32},
        "ecg": load_csv_placeholder(files["ecg"]),
        "resp": load_csv_placeholder(files["resp"]),
        "eda": load_csv_placeholder(files["eda"]),
    }


def export_from_root(input_root: str, output_dir: str):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for record in iter_trial_records(input_root):
        label = load_label_placeholder(record["files"]["label"])
        raw_modalities = build_raw_modalities(record)

        sample_id = f"{record['subject_id']}_{record['trial_id']}_win00"
        sample = build_sample(sample_id, label, raw_modalities)
        export_sample(sample, out_dir)
        total += 1

    return total


def main():
    project_root = Path(__file__).resolve().parents[1]
    input_root = project_root / "data" / "raw"
    output_dir = project_root / "data" / "processed"
    total = export_from_root(str(input_root), str(output_dir))
    print(f"exported {total} samples to {output_dir}")


if __name__ == "__main__":
    main()
