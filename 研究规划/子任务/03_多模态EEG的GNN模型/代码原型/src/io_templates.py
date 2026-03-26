from pathlib import Path
from typing import Dict, List, Iterable


def scan_subject_dirs(root_dir: str) -> List[Path]:
    """
    扫描被试目录。

    预期目录形式：
    root_dir/
      sub01/
      sub02/
      ...
    """
    root = Path(root_dir)
    return sorted([p for p in root.iterdir() if p.is_dir()])


def scan_trial_dirs(subject_dir: Path) -> List[Path]:
    """
    扫描某个被试下的 trial 目录。

    预期目录形式：
    sub01/
      trial01/
      trial02/
      ...
    """
    return sorted([p for p in subject_dir.iterdir() if p.is_dir()])


def build_modalities_file_map(trial_dir: Path) -> Dict[str, Path]:
    """
    构造某个 trial 下各模态文件路径映射。

    你后续需要把这里改成自己的真实命名规则。
    """
    return {
        "eeg": trial_dir / "eeg.csv",
        "ecg": trial_dir / "ecg.csv",
        "resp": trial_dir / "resp.csv",
        "eda": trial_dir / "eda.csv",
        # 未来扩展
        "eye": trial_dir / "eye.csv",
        "egg": trial_dir / "egg.csv",
        "label": trial_dir / "label.json",
    }


def iter_trial_records(root_dir: str) -> Iterable[Dict]:
    """
    遍历整个数据目录，返回 trial 级记录。
    """
    for subject_dir in scan_subject_dirs(root_dir):
        subject_id = subject_dir.name
        for trial_dir in scan_trial_dirs(subject_dir):
            trial_id = trial_dir.name
            yield {
                "subject_id": subject_id,
                "trial_id": trial_id,
                "trial_dir": trial_dir,
                "files": build_modalities_file_map(trial_dir),
            }
