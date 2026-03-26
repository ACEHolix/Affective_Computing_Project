# 单模态 EEG 静态 GCN 伪代码与 PyTorch 草图

## 目标

给出一个足够简单的单模态 EEG 静态 GCN 基线实现草图。

## 伪代码

```python
class EEGStaticGCN(nn.Module):
    def __init__(self, eeg_in_dim, hidden_dim=64, out_dim=3):
        super().__init__()
        self.input_proj = nn.Linear(eeg_in_dim, hidden_dim)
        self.gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.gcn2 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, out_dim)
        )

    def forward(self, x_eeg, adj_eeg):
        h = self.input_proj(x_eeg)
        h = F.relu(self.gcn1(h, adj_eeg))
        h = F.relu(self.gcn2(h, adj_eeg))
        z = h.mean(dim=1)
        y = self.classifier(z)
        return y
```

## 输入约定

- `x_eeg`: `[B, N_eeg, D_eeg]`
- `adj_eeg`: `[B, N_eeg, N_eeg]`

## 最小训练入口

```python
model = EEGStaticGCN(eeg_in_dim=5, hidden_dim=64, out_dim=3)
pred = model(x_eeg, adj_eeg)
loss = criterion(pred, y)
```

## 推荐用途

这个模型应优先用于：

- 单模态图基线
- 和多模态图模型对比
- 和非图 EEG baseline 对比
