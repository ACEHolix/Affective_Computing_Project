# 执行手册

## 当前目标

建立一条从 `Monkey_reward` 远端预处理数据到 `单模态 EEG 静态 GCN` baseline 的最小可执行链路。

## Step 1. 远端路径探测

在 `代码原型` 根目录下执行：

```bash
python scripts/connect_monkey_reward.py --ssh tuoxiaoying@100.92.221.123
```

输出：

- `data/monkey_reward_manifest.json`

## Step 2. 进入远端环境

```bash
bash scripts/try_enter_monkey_env.sh
```

说明：

- 当前脚本默认只检查本机环境
- 真正远端进入环境时，建议直接使用 SSH 执行：

```bash
ssh tuoxiaoying@100.92.221.123 'source ~/senv_auto.sh && python3 --version'
```

## Step 3. 确认日期目录

优先从这些已确认目录开始：

- `20250318`
- `20250502`

## Step 4. 改接入代码

优先要改的代码：

- `src/io_templates.py`
- `src/export_dataset.py`

当前方向：

- 不再按 `sub/trial/csv` 扫描
- 改为按 `Preprocessed Data/<date>/` 扫描

当前 workflow 下已新增专用入口：

- `prepare_dataset.py`
- `train_static_gcn.py`

## Step 5. 导出 baseline 样本

目标：

- 把日期级 EEG 窗口数据导出成适合静态 GCN 的样本格式

建议先只做：

- `x_eeg`
- `adj_eeg`
- `label`
- `date`
- `window_id`

当前可直接使用：

```bash
python prepare_dataset.py \
  --data-root "/home/tuoxiaoying/Documents/Pyproject/Monkey_reward/Preprocessed Data" \
  --output-root "./outputs/monkey_single_eeg_static_gcn" \
  --dates 20250318 20250502
```

## Step 6. 训练 baseline

在当前阶段，先保证：

- 数据能读
- 样本能导出
- baseline 能跑

不要一开始就叠加：

- 多模态
- cross-subject
- 动态图
- 域适应

当前训练入口：

```bash
python train_static_gcn.py \
  --data-dir "./outputs/monkey_single_eeg_static_gcn/20250318" \
  --epochs 10 \
  --num-classes 5 \
  --run-dir "./outputs/experiments/demo_run"
```

## 当前成功标准

如果做到下面这几条，就说明 workflow 第一阶段完成：

1. 可以读取一个真实日期目录
2. 可以生成若干静态 GCN 样本
3. 可以启动单模态 EEG baseline 训练入口

## 当前已完成验证

目前已经在远端真实完成：

1. `20250318` 日期目录样本导出
2. 导出 `1155` 个样本
3. 成功运行 3 个 epoch 的静态 GCN 训练
4. 成功生成 checkpoint、metrics，并回传结果文件到本地

## 正式实验命令

导出正式数据缓存：

```bash
bash run.sh export-formal
```

运行正式实验：

```bash
bash run.sh train-formal run_001 20250318
```

拉回结果文件到本地：

```bash
bash run.sh fetch-results 20250318 run_001
```

当前已经验证可回传的本地结果文件包括：

- `summary.json`
- `history.json`
- `split_indices.json`
