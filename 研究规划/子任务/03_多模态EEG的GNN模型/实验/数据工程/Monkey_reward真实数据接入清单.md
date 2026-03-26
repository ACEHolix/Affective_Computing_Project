# Monkey_reward 真实数据接入清单

## 目的

本文件用于把已经通过 SSH 探查到的 `Monkey_reward` 真实环境信息整理成当前子任务 3 可直接使用的接入清单。

它回答 3 个问题：

1. 真实仓库入口在哪里
2. 真实预处理数据现在长什么样
3. 当前代码原型应该从哪里开始改

## 一、已确认的远端环境信息

通过 SSH 已确认：

- 远端机器：`tuoxiaoying@100.92.221.123`
- 远端仓库：
  - `/home/tuoxiaoying/Documents/Pyproject/Monkey_reward`
- 远端预处理数据目录：
  - `/home/tuoxiaoying/Documents/Pyproject/Monkey_reward/Preprocessed Data`
- 远端输出目录：
  - `/home/tuoxiaoying/Documents/Pyproject/Monkey_reward/outputs`
- 远端容器入口：
  - `/home/tuoxiaoying/senv_auto.sh`

另外已确认：

- 进入容器环境可行
- 容器内可用 `python3`
- 容器内可见 `singularity`

## 二、已确认的 workflow 入口

### 1. 主线 workflow

位置：

- `workflows/mainline_pipeline/`

对应说明：

- `workflows/mainline_pipeline/WORKFLOW.md`
- `workflows/mainline_pipeline/README_pipeline.md`

当前用途：

- `*5.py` 主线训练与预处理流程
- 以日期为单位生成预处理结果

### 2. 对比 workflow

位置：

- `workflows/CNN_Transformer_compare/`

对应说明：

- `workflows/CNN_Transformer_compare/README.md`

当前用途：

- `CNN` 与 `EEG-Conformer` 对比实验
- 独立 workflow 输出目录
- 容器内运行

## 三、已确认的预处理数据结构

当前 `Monkey_reward` 的预处理数据并不是我们本仓库模板里那种：

```text
raw/sub01/trial01/eeg.csv
```

而是更接近：

```text
Preprocessed Data/
  20250318/
    data_values_window.pkl
    data_values_test_window.pkl
    fold_indices_window.pkl
    test_indices_window.pkl
    window_ids_window.pkl
    kept_cols.npy
    meta.json
```

也就是说，**它已经是“按日期组织的预处理产物”**，不是原始 trial 级散文件。

## 四、目前已看到的实际字段

### 1. 日期目录样例

已确认存在：

- `20250318`
- `20250502`

目录内文件包括：

- `data_values_window.pkl`
- `data_values_test_window.pkl`
- `fold_indices_window.pkl`
- `test_indices_window.pkl`
- `window_ids_window.pkl`
- `kept_cols.npy`
- `meta.json`

### 2. meta.json 样例

以 `20250318/meta.json` 为例：

```json
{
  "date": "20250318",
  "variant": "window",
  "C": 58,
  "T": 1000,
  "seconds": 5,
  "sfreq": 200,
  "ds_rate": 10,
  "windows": 11,
  "window_len": 1000,
  "step_len": 200,
  "num_classes": 5
}
```

当前可以直接确认：

- 通道数：`C = 58`
- 每窗口长度：`T = 1000`
- 采样率：`sfreq = 200`
- 当前任务是 `5 分类`
- 当前变体是 `window`

## 五、对当前代码原型的影响

这意味着当前本仓库里原来假设的：

- `sub01/`
- `trial01/`
- `eeg.csv / ecg.csv / resp.csv / eda.csv`

这一套模板并不适合直接对接 `Monkey_reward` 当前已有的预处理数据。

后续接入时，应当分成两条路线：

### 路线 A：对接已有预处理结果

适合现在优先做。

做法：

- 直接读取 `Preprocessed Data/<date>/`
- 从 `pkl/npy/json` 中提取窗口级样本
- 先把已有数据接成单模态 EEG baseline

优点：

- 最快
- 不需要先碰原始 `.mat`
- 更适合作为 baseline 接入

### 路线 B：回到原始数据重新做多模态预处理

适合后续真正做多模态主模型时再推进。

做法：

- 找原始 EEG / ECG / RESP / EDA 数据来源
- 在新 workflow 中补多模态预处理
- 再导出适合本仓库 GNN 原型的样本格式

优点：

- 能真正对接多模态目标

缺点：

- 工程量明显更大

## 六、当前最建议的接入顺序

### 第一阶段：先把已有 EEG 预处理结果接进来

当前最合理。

建议步骤：

1. 新增一个“日期级预处理目录读取器”
2. 先读取 `meta.json`
3. 再读取 `data_values_window.pkl`
4. 明确样本维度、标签位置、fold 结构
5. 先跑通 `单模态 EEG 静态 GCN baseline`

### 第二阶段：再决定多模态怎么补

需要先确认：

- ECG / RESP / EDA 是否已经存在于别处
- 是否已有同步后的预处理版本
- 是否需要新建独立 workflow 做多模态预处理

## 七、当前优先要改的文件

如果按“先接已有 EEG 预处理结果”的路线走，当前最优先要改的是：

- `代码原型/src/io_templates.py`
- `代码原型/src/export_dataset.py`

其中建议新增一套并行逻辑：

- `iter_date_records(...)`
- `load_meta_json(...)`
- `load_preprocessed_window_pkl(...)`

而不是继续沿用 trial 目录扫描方式。

## 八、当前最重要的判断

当前 `Monkey_reward` 的真实数据结构说明了一件事：

**子任务 3 现在最应该先做的是“兼容日期级 EEG 预处理结果”的接入，而不是立刻假设四模态原始文件已经齐全。**

这会更符合实际，也更容易尽快把 baseline 跑起来。
