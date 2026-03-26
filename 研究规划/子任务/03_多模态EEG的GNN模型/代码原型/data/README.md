# 数据目录说明

## 推荐目录结构

```text
data/
  raw/
    sub01/
      trial01/
        eeg.csv
        ecg.csv
        resp.csv
        eda.csv
        label.json
      trial02/
        ...
    sub02/
      ...
  processed/
    sub01_trial01_win00.pt
    sub01_trial02_win00.pt
    ...
  splits/
    subject_dependent_split.json
    subject_independent_split.json
    leave_one_subject_splits.json
```

## 说明

- `raw/` 放原始模态数据
- `processed/` 放预处理后导出的 `.pt` 样本
- `splits/` 放训练/验证/测试划分文件

## 当前脚本对应关系

- `scripts/make_raw_dataset_template.py`
  - 生成最小原始数据目录模板
- `src/export_dataset.py`
  - 从 `raw/` 读取并导出到 `processed/`
- `src/split_dataset.py`
  - 从 `processed/` 生成数据划分文件
- `data/subject_independent_split_template.json`
  - subject-independent 被试划分模板
