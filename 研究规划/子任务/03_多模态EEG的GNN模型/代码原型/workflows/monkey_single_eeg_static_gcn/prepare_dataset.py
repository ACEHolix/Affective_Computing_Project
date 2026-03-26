#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np


def load_meta(date_dir: Path) -> dict:
    with open(date_dir / "meta.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_date_arrays(date_dir: Path):
    with open(date_dir / "data_values_window.pkl", "rb") as f:
        x_train, y_train = pickle.load(f)
    with open(date_dir / "window_ids_window.pkl", "rb") as f:
        window_ids_train, window_ids_test = pickle.load(f)
    with open(date_dir / "test_indices_window.pkl", "rb") as f:
        test_indices_train, test_indices_test = pickle.load(f)

    x_test = None
    y_test = None
    test_file = date_dir / "data_values_test_window.pkl"
    if test_file.exists():
        with open(test_file, "rb") as f:
            x_test, y_test = pickle.load(f)

    return {
        "x_train": x_train,
        "y_train": y_train,
        "x_test": x_test,
        "y_test": y_test,
        "window_ids_train": window_ids_train,
        "window_ids_test": window_ids_test,
        "test_indices_train": test_indices_train,
        "test_indices_test": test_indices_test,
    }


def compute_channel_features(x_sample: np.ndarray) -> np.ndarray:
    if x_sample.ndim == 3:
        x_sample = x_sample[0]
    if x_sample.ndim != 2:
        raise ValueError(f"unexpected sample shape: {x_sample.shape}")

    mean = x_sample.mean(axis=1)
    std = x_sample.std(axis=1)
    vmin = x_sample.min(axis=1)
    vmax = x_sample.max(axis=1)
    energy = (x_sample ** 2).mean(axis=1)
    return np.stack([mean, std, vmin, vmax, energy], axis=1).astype(np.float32)


def build_static_adj(n_channels: int) -> np.ndarray:
    adj = np.eye(n_channels, dtype=np.float32)
    adj += np.ones((n_channels, n_channels), dtype=np.float32) * (1.0 / max(n_channels, 1))
    return adj


def export_date_samples(date_dir: Path, output_root: Path) -> dict:
    meta = load_meta(date_dir)
    arrays = load_date_arrays(date_dir)

    date = meta["date"]
    out_dir = output_root / date
    out_dir.mkdir(parents=True, exist_ok=True)

    x_train = arrays["x_train"]
    y_train = arrays["y_train"]
    adj = build_static_adj(meta["C"])

    exported = 0
    for i in range(len(x_train)):
        sample = {
            "sample_id": f"{date}_train_{i:05d}",
            "date": date,
            "split": "train",
            "window_id": int(arrays["window_ids_train"][i]),
            "test_index": int(arrays["test_indices_train"][i]),
            "label": int(y_train[i]),
            "x_eeg": compute_channel_features(x_train[i]),
            "adj_eeg": adj,
        }
        with open(out_dir / f"{sample['sample_id']}.pkl", "wb") as f:
            pickle.dump(sample, f)
        exported += 1

    if arrays["x_test"] is not None and arrays["y_test"] is not None:
        for i in range(len(arrays["x_test"])):
            sample = {
                "sample_id": f"{date}_test_{i:05d}",
                "date": date,
                "split": "test",
                "window_id": int(arrays["window_ids_test"][i]),
                "test_index": int(arrays["test_indices_test"][i]),
                "label": int(arrays["y_test"][i]),
                "x_eeg": compute_channel_features(arrays["x_test"][i]),
                "adj_eeg": adj,
            }
            with open(out_dir / f"{sample['sample_id']}.pkl", "wb") as f:
                pickle.dump(sample, f)
            exported += 1

    summary = {
        "date": date,
        "meta": meta,
        "num_train": int(len(x_train)),
        "num_test": int(len(arrays["x_test"])) if arrays["x_test"] is not None else 0,
        "output_dir": str(out_dir),
        "num_exported": exported,
        "feature_shape": [meta["C"], 5],
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="导出 Monkey_reward 日期级 EEG 预处理结果为静态 GCN baseline 样本。")
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--dates", nargs="+", required=True)
    args = parser.parse_args()

    data_root = Path(args.data_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    summaries = []
    for date in args.dates:
        summary = export_date_samples(data_root / date, output_root)
        summaries.append(summary)
        print(json.dumps(summary, ensure_ascii=False))

    with open(output_root / "export_manifest.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
