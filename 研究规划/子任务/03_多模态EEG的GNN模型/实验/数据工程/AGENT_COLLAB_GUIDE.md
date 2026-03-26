# Monkey_reward Agent Collaboration Guide

本文件用于和其他 agent / 外部仓库沟通 `Monkey_reward` 仓库的结构、环境、边界和推荐接入方式。

## 1. 仓库定位

`Monkey_reward` 不是单一应用仓库，而是长期演化的科研分析仓库，包含：

- 当前正式 workflow
- 历史实验代码
- 预处理数据
- 模型输出
- 视频处理分支
- MATLAB 分析脚本

默认目标不是继续向仓库根目录堆脚本，而是将新的分析流放到独立 workflow 中。

## 2. 目录概览

### 正式 workflow

- `workflows/mainline_pipeline/`
  - 当前主线 `*5.py` 训练/预处理流程
  - 关键文件：`Preprocessing5.py`、`Dataset5.py`、`Trainer5.py`、`Runner5.py`
  - 常用入口：`run_batch.sh`、`run_batch_windows.bat`

- `workflows/CNN_Transformer_compare/`
  - 完整 `BL / CS / US` 窗口分析流
  - 用于对比 `CNN` 与 `EEG-Conformer`
  - 关键文件：`config.json`、`preprocess.py`、`dataset.py`、`runner.py`、`model_cnn.py`
  - 分析脚本：`analysis/summarize_results.py`、`analysis/plot_results.py`
  - 常用入口：`run.sh`

### 非主线目录

- `legacy/`
  - 历史脚本归档区，只用于参考、结果复现、逻辑对照
  - 不应作为新代码默认依赖来源

- `Preprocessed Data/`
  - 预处理数据目录
  - 按日期分子目录，通常保存 PKL、fold、元数据等

- `outputs/`
  - 训练 checkpoint、汇总结果、图表输出

- `videos_process/`
  - 视频处理与视频模型相关的独立代码和数据

- `matlab/`
  - MATLAB 分析脚本

- `docs/`
  - 说明文档

## 3. 推荐阅读顺序

如果 agent 需要快速理解仓库，建议按以下顺序阅读：

1. `MONKEY_REPO_ANALYSIS_AGENT.md`
2. `workflows/README.md`
3. `workflows/mainline_pipeline/WORKFLOW.md`
4. `workflows/mainline_pipeline/README_pipeline.md`
5. `workflows/CNN_Transformer_compare/README.md`
6. `legacy/README.md`

## 4. 环境与运行约束

### 容器优先

该仓库的真实运行环境是 apptainer / singularity。任何接近真实链路的验证都应优先在容器内完成，例如：

- 导入重依赖训练代码
- 读取真实 `.mat` 数据
- 跑预处理
- 跑训练
- 跑完整评估

可用入口：

- `senv`
- `~/senv_auto.sh`

### 宿主环境适合的事情

宿主环境主要用于：

- 读代码
- 改文本
- git 操作
- 轻量语法检查

如果宿主环境缺包，不应直接断言仓库有问题。先判断该验证是否本来就应在容器内执行。

## 5. 与其他仓库协作的推荐方式

如果其他仓库想“使用这个仓库的环境来分析这个仓库的数据”，推荐方式是：

- 不复制环境
- 不复制数据
- 不直接改写 `Monkey_reward` 主线
- 通过 SSH 登录当前机器后，复用本机已有容器和数据路径

换句话说，优先采用“远程使用现有环境”，而不是“在别的仓库重建一套环境”。

### 推荐模式

其他仓库通过 SSH 到当前主机后：

1. 定位到其自身仓库目录
2. 通过 `senv` 或 `~/senv_auto.sh` 进入容器环境
3. 通过绝对路径引用 `Monkey_reward` 的仓库目录、数据目录和输出目录

建议约定环境变量：

```bash
export MONKEY_REPO=/home/tuoxiaoying/Documents/Pyproject/Monkey_reward
export MONKEY_DATA="$MONKEY_REPO/Preprocessed Data"
export MONKEY_OUTPUT="$MONKEY_REPO/outputs"
```

### SSH 远程调用模板

```bash
ssh user@host '
  export MONKEY_REPO=/home/tuoxiaoying/Documents/Pyproject/Monkey_reward
  export MONKEY_DATA="$MONKEY_REPO/Preprocessed Data"
  export MONKEY_OUTPUT="$MONKEY_REPO/outputs"
  cd /path/to/other_repo
  source ~/senv_auto.sh
  python your_analysis.py --data-root "$MONKEY_DATA"
'
```

## 6. 新需求的落位规则

如果 agent 需要新增分析流：

- 默认新建到 `workflows/<workflow_name>/`
- 不要继续把新 preprocessing / runner / model 直接放仓库根目录
- 不要默认从 `legacy/` import 新生产代码

每个新 workflow 建议至少包含：

- `README.md`
- `TASK_MANUAL.md`
- `preprocess.py`
- `dataset.py`
- `runner.py`
- `run.sh`

如有结构约束，再补：

- `STRATEGY.md`
- `model_*.py`

## 7. 对现有文件的修改边界

默认优先级：

1. 保护主线稳定
2. 避免污染已有 workflow
3. 新实验放到独立 workflow
4. 不混入用户未完成改动

当前应注意：

- `workflows/CNN_Transformer_compare/` 目录下可能存在进行中的本地修改
- 修改前先看 `git status --short`
- 不要擅自回退用户已有未提交变更

## 8. 不推荐做法

- 不要把新分析脚本继续堆到仓库根目录
- 不要因为宿主环境缺包就断言代码不可运行
- 不要把 `legacy/` 当作新功能默认依赖
- 不要把别的仓库和本仓库硬耦合成相互 import 的混乱结构
- 不要复制一份数据和环境再维护第二套

## 9. 给其他 agent 的最短执行建议

如果你是第一次接手这个仓库，先做这几步：

1. 看 `git status --short`
2. 看 `MONKEY_REPO_ANALYSIS_AGENT.md`
3. 看目标 workflow 下的 `README.md` / `TASK_MANUAL.md` / `STRATEGY.md`
4. 判断需求属于主线扩展还是新 workflow
5. 如果涉及真实验证，优先进容器
6. 保持改动独立、路径清晰、git 历史可审计

## 10. 一句话总结

`Monkey_reward` 应被视为“带容器依赖和数据依赖的科研分析母仓库”。其他仓库若要复用它，最佳方式是通过 SSH 在当前机器上直接复用现有环境与数据，而不是复制或重建一套并行环境。
