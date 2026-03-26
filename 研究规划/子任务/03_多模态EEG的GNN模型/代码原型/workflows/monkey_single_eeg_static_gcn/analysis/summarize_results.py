#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def parse_args():
    ap = argparse.ArgumentParser(description="Summarize monkey_single_eeg_static_gcn local result files.")
    ap.add_argument("--results-root", required=True)
    ap.add_argument("--date", default=None)
    return ap.parse_args()


def collect_runs(results_root: Path, date: str | None):
    date_dirs = [results_root / date] if date else [p for p in sorted(results_root.iterdir()) if p.is_dir()]
    rows = []
    for date_dir in date_dirs:
        if not date_dir.exists():
            continue
        for summary_path in sorted(date_dir.glob("**/summary.json")):
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            run_dir = summary_path.parent
            rel_parts = run_dir.relative_to(date_dir).parts
            task_name = payload.get("task")
            if len(rel_parts) >= 2 and rel_parts[0] in {"5cls", "csr_vs_csp", "usr_vs_usp"}:
                task_name = rel_parts[0]
            rows.append({
                "date": date_dir.name,
                "task": task_name,
                "run_name": payload.get("run_name") or run_dir.name,
                "epochs": payload.get("epochs"),
                "best_epoch": payload.get("best_epoch"),
                "best_val_acc": payload.get("best_val_acc"),
                "test_acc": payload.get("test_acc"),
                "test_loss": payload.get("test_loss"),
                "num_train": payload.get("num_train"),
                "num_val": payload.get("num_val"),
                "num_test": payload.get("num_test"),
            })
    return rows


def main():
    args = parse_args()
    results_root = Path(args.results_root)
    rows = collect_runs(results_root, args.date)
    out_json = results_root / ("summary_runs.json" if not args.date else f"summary_runs_{args.date}.json")
    out_csv = results_root / ("summary_runs.csv" if not args.date else f"summary_runs_{args.date}.csv")
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(out_csv, "w", encoding="utf-8") as f:
        f.write("date,run_name,task,epochs,best_epoch,best_val_acc,test_acc,test_loss,num_train,num_val,num_test\n")
        for row in rows:
            f.write(
                f"{row['date']},{row['run_name']},{row['task']},{row['epochs']},{row['best_epoch']},"
                f"{row['best_val_acc']},{row['test_acc']},{row['test_loss']},"
                f"{row['num_train']},{row['num_val']},{row['num_test']}\n"
            )
    print(f"wrote {out_json}")
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
