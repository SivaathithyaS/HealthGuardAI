"""
MRI DenseNet-121 Model Architecture
=====================================
Fine-tuned DenseNet-121 (ImageNet pretrained) for brain tumor classification.

Input  : (batch, 3, 224, 224)  — RGB image (grayscale MRI replicated to 3 channels)
Output : (batch, 4)             — logits for 4 tumor classes

Classes (Kaggle Brain Tumor MRI Dataset — masoudnickparvar):
  0 = glioma
  1 = meningioma
  2 = notumor
  3 = pituitary
"""
import torch
import torch.nn as nn
from torchvision import models


class MRIDenseNet121(nn.Module):
    """
    DenseNet-121 with a replaced classifier head.
    Uses ImageNet pretrained weights from torchvision.
    Accepts (B, 3, 224, 224) — grayscale MRI replicated to 3 channels.
    """
    def __init__(self, num_classes: int = 4, pretrained: bool = True):
        super().__init__()
        self.num_classes = num_classes

        # Load pretrained backbone
        weights = models.DenseNet121_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = models.densenet121(weights=weights)

        # Replace classifier head
        in_features = backbone.classifier.in_features   # 1024 for DenseNet-121
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

    def freeze_backbone(self):
        """Freeze all layers except the classifier head (phase-1 warm-up)."""
        for name, param in self.model.named_parameters():
            if "classifier" not in name:
                param.requires_grad = False

    def unfreeze_all(self):
        """Unfreeze all parameters for full fine-tuning."""
        for param in self.model.parameters():
            param.requires_grad = True


# ── Sanity check ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    model = MRIDenseNet121(num_classes=4, pretrained=False)
    dummy = torch.zeros(2, 3, 224, 224)
    out   = model(dummy)
    total = sum(p.numel() for p in model.parameters())
    print(f"Output shape: {out.shape}")     # (2, 4)
    print(f"Parameters  : {total:,}")       # ~7M
