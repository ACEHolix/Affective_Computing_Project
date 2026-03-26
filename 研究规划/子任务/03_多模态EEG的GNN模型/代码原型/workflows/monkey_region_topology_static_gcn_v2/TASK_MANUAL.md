# 执行手册

## 目标

建立一条：

`Monkey_reward 日期级 EEG 预处理结果 -> 脑区拓扑静态 GCN 第二版 baseline`

的正式实验 workflow。

## 当前模型假设

- `ECoG_01-29` 聚合为一个节点
- `NAc_30-39` 聚合为一个节点
- `AMY_40-49` 聚合为一个节点
- `sgACC_50-54` 聚合为一个节点
- `pgACC_55-64` 聚合为一个节点

实际保留通道以 `kept_cols.npy` 为准。

## 常用命令

查看配置：

```bash
bash run.sh show-config
```

探测远端：

```bash
bash run.sh probe-remote
```

导出 demo 数据：

```bash
bash run.sh export-demo
```

运行 demo：

```bash
bash run.sh train-demo
```

运行正式实验：

```bash
bash run.sh train-formal run_001 20250318
```

拉回结果：

```bash
bash run.sh fetch-results 20250318 run_001
```
