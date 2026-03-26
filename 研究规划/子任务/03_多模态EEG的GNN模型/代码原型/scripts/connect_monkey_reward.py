#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
from typing import Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "monkey_reward_manifest.json"


def candidate_repo_paths() -> List[Path]:
    env_repo = os.environ.get("MONKEY_REPO")
    candidates = []
    if env_repo:
        candidates.append(Path(env_repo).expanduser())
    candidates.extend(
        [
            Path("/home/tuoxiaoying/Documents/Pyproject/Monkey_reward"),
            Path("/Users/tuoxiaoying/Documents/Pyproject/Monkey_reward"),
            Path("/Users/tuoxiaoying/Documents/Work/Repostories/Monkey_reward"),
        ]
    )
    return candidates


def resolve_repo_path(explicit_repo: Optional[str]) -> Optional[Path]:
    if explicit_repo:
        repo = Path(explicit_repo).expanduser()
        return repo if repo.exists() else None

    for path in candidate_repo_paths():
        if path.exists():
            return path
    return None


def resolve_data_path(repo_path: Optional[Path], explicit_data: Optional[str]) -> Optional[Path]:
    if explicit_data:
        path = Path(explicit_data).expanduser()
        return path if path.exists() else None

    env_data = os.environ.get("MONKEY_DATA")
    if env_data:
        path = Path(env_data).expanduser()
        if path.exists():
            return path

    if repo_path is not None:
        for name in ["Preprocessed Data", "preprocessed_data", "data"]:
            path = repo_path / name
            if path.exists():
                return path
    return None


def resolve_output_path(repo_path: Optional[Path], explicit_output: Optional[str]) -> Optional[Path]:
    if explicit_output:
        path = Path(explicit_output).expanduser()
        return path if path.exists() else None

    env_output = os.environ.get("MONKEY_OUTPUT")
    if env_output:
        path = Path(env_output).expanduser()
        if path.exists():
            return path

    if repo_path is not None:
        path = repo_path / "outputs"
        if path.exists():
            return path
    return None


def preview_subdirs(path: Optional[Path], limit: int = 12) -> List[str]:
    if path is None or not path.exists() or not path.is_dir():
        return []
    items = sorted([p.name for p in path.iterdir() if p.is_dir()])
    return items[:limit]


def preview_files(path: Optional[Path], limit: int = 12) -> List[str]:
    if path is None or not path.exists() or not path.is_dir():
        return []
    items = sorted([p.name for p in path.iterdir() if p.is_file()])
    return items[:limit]


def build_manifest(repo_path: Optional[Path], data_path: Optional[Path], output_path: Optional[Path]) -> Dict:
    return {
        "mode": "local",
        "monkey_repo": str(repo_path) if repo_path else None,
        "monkey_data": str(data_path) if data_path else None,
        "monkey_output": str(output_path) if output_path else None,
        "repo_exists": bool(repo_path and repo_path.exists()),
        "data_exists": bool(data_path and data_path.exists()),
        "output_exists": bool(output_path and output_path.exists()),
        "repo_top_level_dirs": preview_subdirs(repo_path),
        "repo_top_level_files": preview_files(repo_path),
        "data_preview_dirs": preview_subdirs(data_path),
        "output_preview_dirs": preview_subdirs(output_path),
        "notes": [
            "本清单只做路径发现和结构预览，不读取真实数据内容。",
            "后续真实接入时，应将这些路径接到 src/io_templates.py 和 src/export_dataset.py。",
        ],
    }


def run_remote_probe(ssh_target: str, repo: Optional[str], data: Optional[str], output: Optional[str]) -> Dict:
    repo_candidate = repo or os.environ.get("MONKEY_REPO") or "/home/tuoxiaoying/Documents/Pyproject/Monkey_reward"
    data_candidate = data or os.environ.get("MONKEY_DATA") or f"{repo_candidate}/Preprocessed Data"
    output_candidate = output or os.environ.get("MONKEY_OUTPUT") or f"{repo_candidate}/outputs"

    remote_script = f"""
set -e
export REPO="{repo_candidate}"
export DATA="{data_candidate}"
export OUTPUT="{output_candidate}"
python3 - <<'PY'
import json
import os
from pathlib import Path

repo = Path(os.environ["REPO"])
data = Path(os.environ["DATA"])
output = Path(os.environ["OUTPUT"])

def preview_subdirs(path, limit=12):
    if not path.exists() or not path.is_dir():
        return []
    return sorted([p.name for p in path.iterdir() if p.is_dir()])[:limit]

def preview_files(path, limit=12):
    if not path.exists() or not path.is_dir():
        return []
    return sorted([p.name for p in path.iterdir() if p.is_file()])[:limit]

manifest = {{
    "mode": "remote",
    "ssh_target": "{ssh_target}",
    "monkey_repo": str(repo),
    "monkey_data": str(data),
    "monkey_output": str(output),
    "repo_exists": repo.exists(),
    "data_exists": data.exists(),
    "output_exists": output.exists(),
    "repo_top_level_dirs": preview_subdirs(repo),
    "repo_top_level_files": preview_files(repo),
    "data_preview_dirs": preview_subdirs(data),
    "output_preview_dirs": preview_subdirs(output),
    "notes": [
        "本清单来自 SSH 远端探测。",
        "路径存在于远端，不代表本机可直接访问这些路径。"
    ],
}}
print(json.dumps(manifest, ensure_ascii=False))
PY
"""

    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=8", ssh_target, remote_script],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="发现 Monkey_reward 仓库与数据路径，并导出清单。")
    parser.add_argument("--repo", type=str, default=None, help="显式指定 MONKEY_REPO 路径")
    parser.add_argument("--data", type=str, default=None, help="显式指定 MONKEY_DATA 路径")
    parser.add_argument("--output", type=str, default=None, help="显式指定 MONKEY_OUTPUT 路径")
    parser.add_argument("--ssh", type=str, default=None, help="通过 SSH 探测远端，例如 user@host")
    parser.add_argument("--manifest", type=str, default=str(DEFAULT_MANIFEST), help="输出清单 JSON 路径")
    args = parser.parse_args()

    if args.ssh:
        manifest = run_remote_probe(args.ssh, args.repo, args.data, args.output)
    else:
        repo_path = resolve_repo_path(args.repo)
        data_path = resolve_data_path(repo_path, args.data)
        output_path = resolve_output_path(repo_path, args.output)
        manifest = build_manifest(repo_path, data_path, output_path)

    manifest_path = Path(args.manifest).expanduser()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"manifest saved to: {manifest_path}")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
