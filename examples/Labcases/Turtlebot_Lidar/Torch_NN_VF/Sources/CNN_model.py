import torch
import torch.nn as nn
import torch.nn.functional as F

class LiDAR_CNN(nn.Module):
    def __init__(self):
        super(LiDAR_CNN, self).__init__()


        self.conv1 = nn.Conv1d(in_channels=1, out_channels=64, kernel_size=7, padding=3)
        self.bn1 = nn.BatchNorm1d(num_features=64)

        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(num_features=128)
        self.pool = nn.MaxPool1d(kernel_size=2)

        self.conv3 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(num_features=256)

        self.gap = nn.AdaptiveAvgPool1d(1)

        self.fc1 = nn.Linear(in_features=256, out_features=128)
        self.dropout = nn.Dropout(0.3)

        self.fc2 = nn.Linear(in_features=128, out_features=1)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.gap(x).squeeze(-1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x
