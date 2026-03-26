# Monkey Single EEG Static GCN Workflow

## 目的

本 workflow 用于把 `Monkey_reward` 现有的 **日期级 EEG 预处理结果** 接到当前项目的 **单模态 EEG 静态 GCN baseline**。

当前目标不是一步到位做完整正式实验，而是先建立一条清晰、独立、可逐步落地的基线 workflow。

## 当前范围

输入来源：

- `Monkey_reward/Preprocessed Data/<date>/`

当前优先支持：

- 单模态 EEG
- 静态图
- 日期级预处理目录
- 5 分类窗口任务

当前暂不直接处理：

- ECG / RESP / EDA
- 原始 `.mat` 级多模态同步预处理
- 动态图
- 正式 cross-subject 多模态主模型

## 推荐执行顺序

1. 先生成远端清单
2. 确认日期目录和字段
3. 做日期级 EEG 数据接入
4. 导出当前 baseline 需要的样本格式
5. 运行静态 GCN baseline

## 主要文件

- `config.json`
  - workflow 配置入口
- `TASK_MANUAL.md`
  - 执行手册
- `prepare_dataset.py`
  - 将 `Preprocessed Data/<date>/` 导出为静态 GCN baseline 样本
- `train_static_gcn.py`
  - 单模态 EEG 静态 GCN 训练入口
- `run.sh`
  - workflow 入口

## 与现有代码的关系

本 workflow 当前主要复用这些代码位置：

- `代码原型/scripts/connect_monkey_reward.py`
- `代码原型/src/io_templates.py`
- `代码原型/src/export_dataset.py`
- `代码原型/src/split_dataset.py`

后续建议新增的专用代码包括：
- 日期级 EEG 数据读取与导出
- 单模态 EEG 静态 GCN 训练入口

## 当前结论

这条 workflow 的意义是：

**先把真实远端 EEG 预处理结果接进来，再跑通单模态 baseline，作为后续多模态 GNN 主模型的真实落地前置。**

## 当前进展

当前已经完成真实验证：

- 已成功通过 SSH 同步 workflow 到远端
- 已成功从 `20250318` 导出静态 GCN baseline 样本
- 已成功启动 `train_static_gcn.py` 并完成 3 个 epoch 的训练
- 已成功把结果文件回传到本地 `results/20250318/demo_20250318/`

当前结果说明：

- 这条 workflow 已经具备最小可执行闭环
- 当前版本已经进一步补上正式实验所需的：
  - 训练/验证划分
  - checkpoint 持久化
  - metrics 输出
  - 本地结果回传

## 输出约定

大文件保存在远端：

- 数据缓存：`/media/tuoxiaoying/DATA/Tuo/Pyproject/Monkey_reward/outputs/monkey_single_eeg_static_gcn/dataset_cache/`
- 实验输出：`/media/tuoxiaoying/DATA/Tuo/Pyproject/Monkey_reward/outputs/monkey_single_eeg_static_gcn/experiments/`

本地只回收结果文件：

- `metrics/summary.json`
- `metrics/history.json`
- `metrics/split_indices.json`

## 工程补全

当前已补：

- `config.py`
- `analysis/summarize_results.py`
- `run.sh show-config`
- `run.sh summarize`

## 当前 smoke run 结果

当前已经完成一轮正式版 smoke run：

- 运行名：`demo_20250318`
- 日期：`20250318`
- 样本总数：`1155`
- 训练集：`832`
- 验证集：`207`
- 测试集：`116`
- 最佳验证 epoch：`1`
- 最佳验证准确率：`0.2415`
- 测试准确率：`0.2931`
