"""
ECG 1D-CNN Model Architecture
==============================
ResNet-style 1D convolutional network for PTB-XL ECG classification.

Input  : (batch, 1, 500)   — single Lead II, 500 samples at 100 Hz = 5 seconds
Output : (batch, 5)         — logits for 5 PTB-XL diagnostic superclasses

PTB-XL Superclass labels (in order):
  0 = NORM   — Normal sinus rhythm
  1 = MI     — Myocardial Infarction
  2 = STTC   — ST/T-wave change (includes ischemia, strain)
  3 = CD     — Conduction disturbance (BBB, AV block, WPW)
  4 = HYP    — Hypertrophy
"""
import torch
import torch.nn as nn


class ResBlock1D(nn.Module):
    """Residual block with two 1D convolutions and optional downsampling."""
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=7,
                               stride=stride, padding=3, bias=False)
        self.bn1   = nn.BatchNorm1d(out_channels)
        self.relu  = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=7,
                               stride=1, padding=3, bias=False)
        self.bn2   = nn.BatchNorm1d(out_channels)

        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1,
                          stride=stride, bias=False),
                nn.BatchNorm1d(out_channels)
            )

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample:
            identity = self.downsample(x)
        return self.relu(out + identity)


class ECGResNet1D(nn.Module):
    """
    1D ResNet for single-lead ECG classification.
    ~1.2M parameters.  Input: (B, 1, 500).  Output: (B, num_classes).
    """
    def __init__(self, num_classes: int = 5):
        super().__init__()
        self.num_classes = num_classes

        # Initial stem
        self.stem = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=15, stride=2, padding=7, bias=False),  # → (B, 32, 250)
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=3, stride=2, padding=1)                     # → (B, 32, 125)
        )

        # Residual stages
        self.layer1 = self._make_layer(32,  64, num_blocks=2, stride=1)  # → (B, 64, 125)
        self.layer2 = self._make_layer(64, 128, num_blocks=2, stride=2)  # → (B,128,  63)
        self.layer3 = self._make_layer(128, 256, num_blocks=2, stride=2) # → (B,256,  32)
        self.layer4 = self._make_layer(256, 512, num_blocks=2, stride=2) # → (B,512,  16)

        self.global_pool = nn.AdaptiveAvgPool1d(1)   # → (B, 512, 1)
        self.dropout      = nn.Dropout(p=0.3)
        self.classifier   = nn.Linear(512, num_classes)

    def _make_layer(self, in_ch, out_ch, num_blocks, stride):
        layers = [ResBlock1D(in_ch, out_ch, stride=stride)]
        for _ in range(1, num_blocks):
            layers.append(ResBlock1D(out_ch, out_ch, stride=1))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.stem(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.global_pool(x).squeeze(-1)
        x = self.dropout(x)
        return self.classifier(x)


# ── Sanity check ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    model = ECGResNet1D(num_classes=5)
    dummy = torch.zeros(4, 1, 500)
    out = model(dummy)
    total = sum(p.numel() for p in model.parameters())
    print(f"Output shape : {out.shape}")   # (4, 5)
    print(f"Parameters   : {total:,}")     # ~1.2M
