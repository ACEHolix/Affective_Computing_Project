import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleGraphConv(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)

    def forward(self, x, adj):
        h = torch.bmm(adj, x)
        return self.linear(h)


class MultiModalEEGGNN(nn.Module):
    def __init__(self, eeg_in_dim, phy_in_dim, hidden_dim=64, out_dim=3, dropout=0.3):
        super().__init__()
        self.eeg_proj = nn.Linear(eeg_in_dim, hidden_dim)
        self.phy_proj = nn.Linear(phy_in_dim, hidden_dim)

        self.eeg_gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.eeg_gcn2 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.phy_gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)
        self.cross_gcn1 = SimpleGraphConv(hidden_dim, hidden_dim)

        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, x_eeg, x_phy, adj_eeg, adj_phy, adj_cross):
        h_eeg = F.relu(self.eeg_proj(x_eeg))
        h_phy = F.relu(self.phy_proj(x_phy))

        h_eeg = F.relu(self.eeg_gcn1(h_eeg, adj_eeg))
        h_eeg = F.relu(self.eeg_gcn2(h_eeg, adj_eeg))

        h_phy = F.relu(self.phy_gcn1(h_phy, adj_phy))

        h_all = torch.cat([h_eeg, h_phy], dim=1)
        h_all = F.relu(self.cross_gcn1(h_all, adj_cross))

        z = h_all.mean(dim=1)
        return self.classifier(z)
