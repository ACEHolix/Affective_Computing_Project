#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np


REGION_RANGES = {
    "ECoG": range(0, 29),
    "NAc": range(29, 39),
    "AMY": range(39, 49),
    "sgACC": range(49, 54),
    "pgACC": range(54, 64),
}
REGION_ORDER = ["ECoG", "NAc", "AMY", "sgACC", "pgACC"]


def load_meta(date_dir: Path) -> dict:
    with open(date_dir / "meta.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_kept_cols(date_dir: Path) -> np.ndarray:
    return np.load(date_dir / "kept_cols.npy")


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


def build_region_index_map(kept_cols: np.ndarray):
    mapping = {}
    for region in REGION_ORDER:
        ids = list(REGION_RANGES[region])
        positions = [i for i, col_id in enumerate(kept_cols.tolist()) if col_id in ids]
        mapping[region] = positions
    return mapping


def compute_region_features(x_sample: np.ndarray, region_index_map: dict) -> np.ndarray:
    if x_sample.ndim == 3:
        x_sample = x_sample[0]
    if x_sample.ndim != 2:
        raise ValueError(f"unexpected sample shape: {x_sample.shape}")

    features = []
    for region in REGION_ORDER:
        idxs = region_index_map[region]
        if not idxs:
            region_signal = np.zeros((1, x_sample.shape[1]), dtype=np.float32)
        else:
            region_signal = x_sample[idxs, :]
        mean = region_signal.mean()
        std = region_signal.std()
        vmin = region_signal.min()
        vmax = region_signal.max()
        energy = (region_signal ** 2).mean()
        features.append([mean, std, vmin, vmax, energy])
    return np.asarray(features, dtype=np.float32)


def build_region_adj() -> np.ndarray:
    return np.asarray(
        [
            [1.0, 0.4, 0.4, 0.7, 0.7],
            [0.4, 1.0, 0.8, 0.6, 0.6],
            [0.4, 0.8, 1.0, 0.6, 0.6],
            [0.7, 0.6, 0.6, 1.0, 0.9],
            [0.7, 0.6, 0.6, 0.9, 1.0],
        ],
        dtype=np.float32,
    )


def export_date_samples(date_dir: Path, output_root: Path) -> dict:
    meta = load_meta(date_dir)
    kept_cols = load_kept_cols(date_dir)
    arrays = load_date_arrays(date_dir)
    region_index_map = build_region_index_map(kept_cols)
    adj = build_region_adj()

    date = meta["date"]
    out_dir = output_root / date
    out_dir.mkdir(parents=True, exist_ok=True)

    exported = 0
    for i in range(len(arrays["x_train"])):
        sample = {
            "sample_id": f"{date}_train_{i:05d}",
            "date": date,
            "split": "train",
            "window_id": int(arrays["window_ids_train"][i]),
            "test_index": int(arrays["test_indices_train"][i]),
            "label": int(arrays["y_train"][i]),
            "x_eeg": compute_region_features(arrays["x_train"][i], region_index_map),
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
                "x_eeg": compute_region_features(arrays["x_test"][i], region_index_map),
                "adj_eeg": adj,
            }
            with open(out_dir / f"{sample['sample_id']}.pkl", "wb") as f:
                pickle.dump(sample, f)
            exported += 1

    summary = {
        "date": date,
        "meta": meta,
        "kept_cols": kept_cols.tolist(),
        "region_index_map": region_index_map,
        "region_order": REGION_ORDER,
        "num_exported": exported,
        "feature_shape": [5, 5],
        "output_dir": str(out_dir),
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def main():
    parser = argparse.ArgumentParser(description="导出脑区拓扑静态 GCN 第二版样本。")
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--dates", nargs="+", required=True)
    args = parser.parse_args()

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    summaries = []
    for date in args.dates:
        summary = export_date_samples(Path(args.data_root) / date, output_root)
        summaries.append(summary)
        print(json.dumps(summary, ensure_ascii=False))
    with open(output_root / "export_manifest.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
