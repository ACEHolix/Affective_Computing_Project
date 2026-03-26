#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_DIR="$(cd "$(dirname "$0")" && pwd)"
PROTO_ROOT="$(cd "$WORKFLOW_DIR/../.." && pwd)"
CONFIG="$WORKFLOW_DIR/config.json"
PYTHON_BIN=${PYTHON_BIN:-python3}
SSH_TARGET="tuoxiaoying@100.92.221.123"
REMOTE_WORKFLOW_DIR="/home/tuoxiaoying/tmp/affective_computing_review/monkey_region_topology_static_gcn_v2"
REMOTE_DATASET_CACHE="/media/tuoxiaoying/DATA/Tuo/Pyproject/Monkey_reward/outputs/monkey_region_topology_static_gcn_v2/dataset_cache"
REMOTE_EXPERIMENT_ROOT="/media/tuoxiaoying/DATA/Tuo/Pyproject/Monkey_reward/outputs/monkey_region_topology_static_gcn_v2/experiments"
LOCAL_RESULTS_DIR="$WORKFLOW_DIR/results"

cmd="${1:-show-config}"

case "$cmd" in
  show-config)
    "$PYTHON_BIN" - <<PY
import sys
sys.path.insert(0, r"$WORKFLOW_DIR")
from config import load_workflow_config, pretty_json
cfg, _ = load_workflow_config(r"$CONFIG")
print(pretty_json(cfg))
PY
    ;;
  probe-remote)
    python3 "$PROTO_ROOT/scripts/connect_monkey_reward.py" --ssh "$SSH_TARGET"
    ;;
  sync-remote)
    ssh "$SSH_TARGET" "mkdir -p '$REMOTE_WORKFLOW_DIR'"
    scp "$WORKFLOW_DIR/prepare_dataset_v2.py" "$SSH_TARGET:$REMOTE_WORKFLOW_DIR/"
    scp "$WORKFLOW_DIR/train_region_static_gcn.py" "$SSH_TARGET:$REMOTE_WORKFLOW_DIR/"
    scp "$WORKFLOW_DIR/config.json" "$SSH_TARGET:$REMOTE_WORKFLOW_DIR/"
    echo "synced to $SSH_TARGET:$REMOTE_WORKFLOW_DIR"
    ;;
  export-demo)
    bash "$0" sync-remote
    ssh "$SSH_TARGET" "source ~/senv_auto.sh && mkdir -p '$REMOTE_DATASET_CACHE' && cd '$REMOTE_WORKFLOW_DIR' && python3 prepare_dataset_v2.py --data-root '/home/tuoxiaoying/Documents/Pyproject/Monkey_reward/Preprocessed Data' --output-root '$REMOTE_DATASET_CACHE' --dates 20250318"
    ;;
  train-demo)
    bash "$0" export-demo
    bash "$0" sync-remote
    ssh "$SSH_TARGET" "source ~/senv_auto.sh && mkdir -p '$REMOTE_EXPERIMENT_ROOT/20250318/demo_v2_20250318' && cd '$REMOTE_WORKFLOW_DIR' && python3 train_region_static_gcn.py --data-dir '$REMOTE_DATASET_CACHE/20250318' --epochs 3 --num-classes 5 --run-dir '$REMOTE_EXPERIMENT_ROOT/20250318/demo_v2_20250318'"
    ;;
  train-formal)
    RUN_NAME="${2:-run_001}"
    DATE_NAME="${3:-20250318}"
    bash "$0" sync-remote
    ssh "$SSH_TARGET" "source ~/senv_auto.sh && mkdir -p '$REMOTE_DATASET_CACHE' && cd '$REMOTE_WORKFLOW_DIR' && python3 prepare_dataset_v2.py --data-root '/home/tuoxiaoying/Documents/Pyproject/Monkey_reward/Preprocessed Data' --output-root '$REMOTE_DATASET_CACHE' --dates '$DATE_NAME'"
    ssh "$SSH_TARGET" "source ~/senv_auto.sh && mkdir -p '$REMOTE_EXPERIMENT_ROOT/$DATE_NAME/$RUN_NAME' && cd '$REMOTE_WORKFLOW_DIR' && python3 train_region_static_gcn.py --data-dir '$REMOTE_DATASET_CACHE/$DATE_NAME' --epochs 20 --batch-size 32 --hidden-dim 64 --num-classes 5 --dropout 0.3 --learning-rate 0.001 --val-ratio 0.2 --seed 42 --run-dir '$REMOTE_EXPERIMENT_ROOT/$DATE_NAME/$RUN_NAME'"
    ;;
  fetch-results)
    RUN_DATE="${2:-20250318}"
    RUN_NAME="${3:-run_001}"
    mkdir -p "$LOCAL_RESULTS_DIR/$RUN_DATE/$RUN_NAME"
    scp "$SSH_TARGET:$REMOTE_EXPERIMENT_ROOT/$RUN_DATE/$RUN_NAME/metrics/summary.json" "$LOCAL_RESULTS_DIR/$RUN_DATE/$RUN_NAME/" || true
    scp "$SSH_TARGET:$REMOTE_EXPERIMENT_ROOT/$RUN_DATE/$RUN_NAME/metrics/history.json" "$LOCAL_RESULTS_DIR/$RUN_DATE/$RUN_NAME/" || true
    scp "$SSH_TARGET:$REMOTE_EXPERIMENT_ROOT/$RUN_DATE/$RUN_NAME/metrics/split_indices.json" "$LOCAL_RESULTS_DIR/$RUN_DATE/$RUN_NAME/" || true
    echo "fetched results to $LOCAL_RESULTS_DIR/$RUN_DATE/$RUN_NAME"
    ;;
  summarize)
    RESULTS_DATE="${2:-}"
    cmd=("$PYTHON_BIN" "$WORKFLOW_DIR/analysis/summarize_results.py" --results-root "$LOCAL_RESULTS_DIR")
    if [[ -n "$RESULTS_DATE" ]]; then cmd+=(--date "$RESULTS_DATE"); fi
    "${cmd[@]}"
    ;;
  *)
    echo "unknown command: $cmd"
    echo "available: show-config | probe-remote | sync-remote | export-demo | train-demo | train-formal [run_name] [date] | fetch-results [date] [run_name] | summarize [date]"
    exit 1
    ;;
esac
