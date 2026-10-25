"""
Neural Network Architectures for ECG and MRI Inference
======================================================
Contains:
  - ResBlock1D, ECGResNet1D: 1D-CNN ResNet for PTB-XL ECG classification (5 classes)
  - MRIDenseNet121: DenseNet-121 fine-tuned for brain tumor classification (4 classes)

Also registers itself as `model` in sys.modules so PyTorch checkpoints saved
with torch.save(model) can unpickle cleanly across processes.
"""
import sys
import types
import torch
import torch.nn as nn
from torchvision import models


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
    Input: (B, 1, 500). Output: (B, num_classes).
    """
    def __init__(self, num_classes: int = 5):
        super().__init__()
        self.num_classes = num_classes

        # Initial stem
        self.stem = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=15, stride=2, padding=7, bias=False),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        )

        # Residual stages
        self.layer1 = self._make_layer(32,  64, num_blocks=2, stride=1)
        self.layer2 = self._make_layer(64, 128, num_blocks=2, stride=2)
        self.layer3 = self._make_layer(128, 256, num_blocks=2, stride=2)
        self.layer4 = self._make_layer(256, 512, num_blocks=2, stride=2)

        self.global_pool = nn.AdaptiveAvgPool1d(1)
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


class MRIDenseNet121(nn.Module):
    """
    DenseNet-121 with custom classifier head for MRI brain tumor classification.
    Input: (B, 3, 224, 224). Output: (B, 4).
    """
    def __init__(self, num_classes: int = 4, pretrained: bool = False):
        super().__init__()
        self.num_classes = num_classes

        backbone = models.densenet121(weights=None)
        in_features = backbone.classifier.in_features
        backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(512, num_classes)
        )
        self.model = backbone

    def forward(self, x):
        return self.model(x)


def register_model_globals():
    """
    Registers ResBlock1D, ECGResNet1D, and MRIDenseNet121 under the synthetic
    module name 'model' in sys.modules so PyTorch checkpoints can unpickle.
    Also adds them to PyTorch 2.6 safe_globals if available.
    """
    curr_mod = sys.modules[__name__]
    if "model" not in sys.modules:
        synthetic_mod = types.ModuleType("model")
        synthetic_mod.ResBlock1D = ResBlock1D
        synthetic_mod.ECGResNet1D = ECGResNet1D
        synthetic_mod.MRIDenseNet121 = MRIDenseNet121
        sys.modules["model"] = synthetic_mod
    else:
        m = sys.modules["model"]
        m.ResBlock1D = ResBlock1D
        m.ECGResNet1D = ECGResNet1D
        m.MRIDenseNet121 = MRIDenseNet121

    # Register safe globals for PyTorch 2.6+ if supported
    try:
        import torch.serialization
        if hasattr(torch.serialization, "add_safe_globals"):
            torch.serialization.add_safe_globals([ResBlock1D, ECGResNet1D, MRIDenseNet121])
    except Exception:
        pass


# Automatically register on import
register_model_globals()
