# Monkey Region Topology Static GCN V2

## 目的

本 workflow 是单模态 EEG 静态 GCN 的第二版。

与第一版的核心差异在于：

- 第一版：保留通道级节点
- 第二版：按脑区拓扑聚合成区域级节点

## 节点定义

固定 5 个节点：

1. `ECoG`
2. `NAc`
3. `AMY`
4. `sgACC`
5. `pgACC`

## 设计原则

- `ECoG` 表面分布未知，不强行假设表面电极几何位置
- 深部电极按脑区聚合
- 图结构使用脑区拓扑先验
- 仍保持静态图，便于与第一版 baseline 直接比较

## 输出策略

大文件保存在远端：

- `/media/tuoxiaoying/DATA/Tuo/Pyproject/Monkey_reward/outputs/monkey_region_topology_static_gcn_v2/`

本地只接收结果文件：

- `summary.json`
- `history.json`
- `split_indices.json`

## 工程补全

当前已补：

- `config.py`
- `analysis/summarize_results.py`
- `run.sh show-config`
- `run.sh summarize`

## 当前用途

这条线的主要作用是：

**验证“脑区级拓扑图”是否优于第一版粗粒度通道静态图 baseline。**
