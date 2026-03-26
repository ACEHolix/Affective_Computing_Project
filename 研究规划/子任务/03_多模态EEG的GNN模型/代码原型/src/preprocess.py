from pathlib import Path
import torch


class PreprocessConfig:
    def __init__(self, window_length=4, step_length=2):
        self.window_length = window_length
        self.step_length = step_length


def preprocess_eeg(raw_eeg):
    """
    占位函数：
    这里后续接入 EEG 滤波、分段和频带特征提取。
    当前返回 dummy 通道特征。
    """
    n_channels = raw_eeg.get("n_channels", 32)
    return torch.randn(n_channels, 5)


def preprocess_ecg(raw_ecg):
    """
    占位函数：
    后续接入 ECG 峰检测和 HR/HRV 特征。
    """
    return torch.randn(4)


def preprocess_resp(raw_resp):
    """
    占位函数：
    后续接入 RESP 呼吸频率和振幅特征。
    """
    return torch.randn(4)


def preprocess_eda(raw_eda):
    """
    占位函数：
    后续接入 EDA tonic/phasic 特征。
    """
    return torch.randn(4)


def build_eeg_adj(n_eeg):
    return torch.eye(n_eeg)


def build_phy_adj(n_phy):
    return torch.ones(n_phy, n_phy)


def build_cross_adj(n_all):
    return torch.ones(n_all, n_all)


def build_sample(sample_id, label, raw_modalities):
    x_eeg = preprocess_eeg(raw_modalities["eeg"])
    x_ecg = preprocess_ecg(raw_modalities["ecg"])
    x_resp = preprocess_resp(raw_modalities["resp"])
    x_eda = preprocess_eda(raw_modalities["eda"])

    x_phy = torch.stack([x_ecg, x_resp, x_eda], dim=0)
    n_eeg = x_eeg.shape[0]
    n_phy = x_phy.shape[0]

    sample = {
        "sample_id": sample_id,
        "subject_id": raw_modalities.get("subject_id", "unknown"),
        "trial_id": raw_modalities.get("trial_id", "unknown"),
        "window_id": raw_modalities.get("window_id", 0),
        "label": label,
        "x_eeg": x_eeg,
        "x_phy": x_phy,
        "adj_eeg": build_eeg_adj(n_eeg),
        "adj_phy": build_phy_adj(n_phy),
        "adj_cross": build_cross_adj(n_eeg + n_phy),
    }
    return sample


def export_sample(sample, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{sample['sample_id']}.pt"
    torch.save(sample, out_path)
    return out_path


def main():
    """
    当前只是预处理骨架示例。
    后续要替换成真实数据读取逻辑。
    """
    dummy_raw = {
        "subject_id": "sub01",
        "trial_id": "trial01",
        "window_id": 0,
        "eeg": {"n_channels": 32},
        "ecg": {},
        "resp": {},
        "eda": {},
    }
    sample = build_sample("sub01_trial01_win00", 0, dummy_raw)
    out_path = export_sample(sample, Path(__file__).resolve().parents[1] / "data")
    print(f"sample exported to: {out_path}")


if __name__ == "__main__":
    main()
