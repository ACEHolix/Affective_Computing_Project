# 第一版模型伪代码与PyTorch草图

## 目标

本文件给出一个可直接作为第一版实现参考的模型草图。

目标模型仍然是：

- EEG 图
- 外周生理图
- 跨模态融合图
- 样本级情感分类输出

这里先用 **PyTorch 风格伪代码** 表达结构，不强依赖某个具体图学习库。

如果后续正式实现，建议优先使用：

- `torch`
- `torch_geometric`

## 一、输入约定

假设一个 batch 的输入为：

- `x_eeg`: EEG 节点特征，形状约为 `[B, N_eeg, D_eeg]`
- `x_phy`: 外周节点特征，形状约为 `[B, N_phy, D_phy]`
- `adj_eeg`: EEG 图邻接矩阵，形状约为 `[B, N_eeg, N_eeg]`
- `adj_phy`: 外周图邻接矩阵，形状约为 `[B, N_phy, N_phy]`
- `adj_cross`: 跨模态图邻接矩阵，形状约为 `[B, N_all, N_all]`

其中：

- `N_eeg = EEG通道数`
- `N_phy = 3`，分别对应 ECG / RESP / EDA
- `N_all = N_eeg + N_phy`

## 二、模型模块划分

模型建议拆成 4 个模块：

1. 节点特征投影层
2. EEG 图编码器
3. 外周图编码器
4. 跨模态图融合与分类头

## 三、简化版图卷积层伪代码

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleGraphConv(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)

    def forward(self, x, adj):
        # x: [B, N, D]
        # adj: [B, N, N]
        h = torch.bmm(adj, x)
        h = self.linear(h)
        return h
```

这只是最小表达。  
正式实现时建议换成：

- `GCNConv`
- `GATConv`
- `GraphConv`

## 四、第一版模型草图

```python
class MultiModalEEGGNN(nn.Module):
    def __init__(
        self,
        eeg_in_dim,
        phy_in_dim,
        hidden_dim=64,
        out_dim=3
    ):
        super().__init__()

        # 1. 输入投影
        self.eeg_proj = nn.Linear(eeg_in_dim, hidden_dim)
        self.phy_proj = nn.Linear(phy_in_dim, hidden_dim)

        # 2. EEG 图编码器
        self.eeg_gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.eeg_gcn2 = SimpleGraphConv(hidden_dim, hidden_dim)

        # 3. 外周图编码器
        self.phy_gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)

        # 4. 跨模态图融合
        self.cross_gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)

        # 5. 分类头
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, out_dim)
        )

    def forward(self, x_eeg, x_phy, adj_eeg, adj_phy, adj_cross):
        # x_eeg: [B, N_eeg, D_eeg]
        # x_phy: [B, N_phy, D_phy]

        # Step 1: 输入投影
        h_eeg = self.eeg_proj(x_eeg)
        h_phy = self.phy_proj(x_phy)

        # Step 2: EEG 图编码
        h_eeg = self.eeg_gcn1(h_eeg, adj_eeg)
        h_eeg = F.relu(h_eeg)
        h_eeg = self.eeg_gcn2(h_eeg, adj_eeg)
        h_eeg = F.relu(h_eeg)

        # Step 3: 外周图编码
        h_phy = self.phy_gcn1(h_phy, adj_phy)
        h_phy = F.relu(h_phy)

        # Step 4: 拼接为跨模态节点集合
        h_all = torch.cat([h_eeg, h_phy], dim=1)

        # Step 5: 跨模态图融合
        h_all = self.cross_gcn1(h_all, adj_cross)
        h_all = F.relu(h_all)

        # Step 6: 图级读出
        z = h_all.mean(dim=1)

        # Step 7: 分类输出
        y = self.classifier(z)
        return y
```

## 五、训练循环草图

```python
model = MultiModalEEGGNN(
    eeg_in_dim=D_eeg,
    phy_in_dim=D_phy,
    hidden_dim=64,
    out_dim=num_classes
)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

for epoch in range(num_epochs):
    model.train()
    for batch in train_loader:
        x_eeg = batch["x_eeg"]
        x_phy = batch["x_phy"]
        adj_eeg = batch["adj_eeg"]
        adj_phy = batch["adj_phy"]
        adj_cross = batch["adj_cross"]
        y = batch["label"]

        pred = model(x_eeg, x_phy, adj_eeg, adj_phy, adj_cross)
        loss = criterion(pred, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

## 六、推荐的数据组织格式

每个样本建议组织成：

```python
sample = {
    "x_eeg": Tensor[N_eeg, D_eeg],
    "x_phy": Tensor[N_phy, D_phy],
    "adj_eeg": Tensor[N_eeg, N_eeg],
    "adj_phy": Tensor[N_phy, N_phy],
    "adj_cross": Tensor[N_all, N_all],
    "label": int
}
```

## 七、第一版实现建议

### 1. 先固定外周模态节点数

第一版建议：

- ECG 一个节点
- RESP 一个节点
- EDA 一个节点

不要一开始就把每个模态拆成很多节点。

### 2. 先固定邻接矩阵

第一版建议：

- EEG 图：固定空间邻接
- 外周图：三节点全连接
- 跨模态图：EEG 全连接到各外周节点

先不要一开始就做可学习邻接矩阵。

### 3. 先做分类任务

建议：

- 三分类或二分类

## 八、后续升级接口

这个草图后续可以很自然升级为：

### 升级 1：把 `SimpleGraphConv` 换成 `GATConv`

这样就得到：

- 图注意力多模态模型

### 升级 2：把跨模态边改成可学习边权

这样就得到：

- 更灵活的跨模态融合

### 升级 3：引入 cross-subject 训练与域适应模块

### 升级 4：加入眼动节点

### 升级 5：视情况加入 EGG 节点

## 九、如果用 PyTorch Geometric 实现

后续如果正式写代码，建议考虑：

- `torch_geometric.nn.GCNConv`
- `torch_geometric.nn.GATConv`
- `torch_geometric.nn.global_mean_pool`

因为：

- 实现更标准
- 后续换模型更方便

## 十、当前结论

这份草图已经足够作为第一版代码实现的结构参考。

如果后续继续推进，下一步最适合补的是：

- `数据预处理与特征提取实施方案`
- 或 `数据样本组织格式示例`
