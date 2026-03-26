from pathlib import Path
import json
import random


def collect_processed_files(processed_dir: str):
    return sorted(Path(processed_dir).glob("*.pt"))


def parse_subject_id(file_path: Path):
    name = file_path.stem
    # 预期格式：sub01_trial01_win00
    return name.split("_")[0]


def split_subject_dependent(files, train_ratio=0.7, val_ratio=0.15, seed=42):
    rng = random.Random(seed)
    files = list(files)
    rng.shuffle(files)

    n = len(files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train_files = files[:n_train]
    val_files = files[n_train:n_train + n_val]
    test_files = files[n_train + n_val:]
    return train_files, val_files, test_files


def split_subject_independent(files, train_subjects, val_subjects=None):
    val_subjects = set(val_subjects or [])
    train_subjects = set(train_subjects)

    train_files, val_files, test_files = [], [], []
    for file_path in files:
        subject_id = parse_subject_id(file_path)
        if subject_id in train_subjects:
            train_files.append(file_path)
        elif subject_id in val_subjects:
            val_files.append(file_path)
        else:
            test_files.append(file_path)
    return train_files, val_files, test_files


def dump_split(train_files, val_files, test_files, out_path: str):
    split_info = {
        "train": [str(p) for p in train_files],
        "val": [str(p) for p in val_files],
        "test": [str(p) for p in test_files],
    }
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(split_info, f, ensure_ascii=False, indent=2)
    return out_path


def main():
    project_root = Path(__file__).resolve().parents[1]
    processed_dir = project_root / "data" / "processed"
    split_dir = project_root / "data" / "splits"

    files = collect_processed_files(processed_dir)

    # 第一版默认做 subject-dependent 随机划分
    train_files, val_files, test_files = split_subject_dependent(files)
    out_path = dump_split(
        train_files,
        val_files,
        test_files,
        split_dir / "subject_dependent_split.json"
    )
    print(f"split saved to: {out_path}")


if __name__ == "__main__":
    main()
