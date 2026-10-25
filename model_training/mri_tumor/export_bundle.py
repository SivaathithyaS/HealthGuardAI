"""
MRI Bundle Exporter
====================
Run after train_mri.py:
    python export_bundle.py

Produces ../output/mri_cnn/ containing:
    weights.pt       — full torch.save(model)
    config.json      — 4 tumor classes, sha256, stub=false
    preprocess.py    — updated for 224×224 RGB normalisation
    MODEL_CARD.md    — training metadata
"""
import os
import sys
import json
import shutil
import hashlib
import torch

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
CKPT_DIR     = os.path.join(SCRIPT_DIR, "checkpoints")
OUTPUT_DIR   = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "output", "mri_cnn"))
MODEL_PT     = os.path.join(CKPT_DIR, "best_mri_model.pt")
METRICS_JSON = os.path.join(CKPT_DIR, "eval_metrics.json")

if not os.path.exists(MODEL_PT):
    print(f"ERROR: {MODEL_PT} not found. Run train_mri.py first.")
    sys.exit(1)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Copy weights ──────────────────────────────────────────────────────────────
weights_dest = os.path.join(OUTPUT_DIR, "weights.pt")
shutil.copy2(MODEL_PT, weights_dest)
with open(weights_dest, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
print(f"weights.pt SHA-256: {sha256}")

# ── Load metrics ──────────────────────────────────────────────────────────────
metrics = {}
if os.path.exists(METRICS_JSON):
    with open(METRICS_JSON) as f:
        metrics = json.load(f)

# ── Labels ────────────────────────────────────────────────────────────────────
# Human-readable clinical equivalents matching the Kaggle classes
LABELS = [
    "Glioma / High-Grade Neoplasm",      # glioma
    "Meningioma",                         # meningioma
    "No Tumor Detected",                  # notumor
    "Pituitary Adenoma"                   # pituitary
]

# ── config.json ───────────────────────────────────────────────────────────────
config = {
    "name":          "mri_cnn",
    "modality":      "mri",
    "model_version": "mri-densenet121-kaggle-v1",
    "stub":          False,
    "threshold":     0.60,
    "num_classes":   4,
    "input_shape":   [3, 224, 224],
    "weights_file":  "weights.pt",
    "weights_sha256": sha256,
    "labels": LABELS,
    "description": (
        "DenseNet-121 fine-tuned on the Kaggle Brain Tumor MRI Dataset "
        "(masoudnickparvar, 7,023 images). Classifies axial MRI slices "
        "into 4 categories: glioma, meningioma, no-tumor, and pituitary adenoma."
    ),
    "training": {
        "dataset":        "Kaggle Brain Tumor MRI Dataset (masoudnickparvar)",
        "n_train":        "~2,870 images (Training split)",
        "n_test":         "~394 images (Testing split)",
        "val_accuracy":   metrics.get("best_val_acc", "see MODEL_CARD.md"),
        "test_accuracy":  metrics.get("test_accuracy", "see MODEL_CARD.md"),
        "note": ("WARNING: 'notumor' class comes from a different image source. "
                 "Check domain_bias_report.json for brightness statistics.")
    }
}

with open(os.path.join(OUTPUT_DIR, "config.json"), "w") as f:
    json.dump(config, f, indent=2)
print("Written config.json")

# ── preprocess.py — updated for real model ────────────────────────────────────
preprocess_code = '''"""
Brain MRI Preprocessor for HealthGuard AI DenseNet-121 (real model).
Reads any PNG/JPG/TIFF image, converts to 3-channel RGB (grayscale × 3),
resizes to 224×224, and applies ImageNet normalisation.

Output contract (matches DenseNet-121 training):
  pixel_tensor: list of shape [3, 224, 224] — ImageNet-normalised float32
  original_size: (W, H)
  target_size:   (224, 224)
  channels:      3
  mean_intensity: float  (grayscale mean before normalisation)
  variance:       float
"""
import io
import numpy as np
from PIL import Image

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
TARGET_SIZE   = (224, 224)


def preprocess(raw_bytes: bytes, filename: str = "") -> dict:
    if not raw_bytes or len(raw_bytes) == 0:
        raise ValueError("MRI image file is empty (0 bytes received).")

    if b"CORRUPT" in raw_bytes or b"INVALID_DICOM" in raw_bytes:
        raise ValueError("Corrupted MRI file header detected.")

    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img.verify()
        img = Image.open(io.BytesIO(raw_bytes))
    except Exception as e:
        raise ValueError(f"Invalid MRI image: {e}. Supported: PNG, JPG, TIFF.")

    if img.width < 16 or img.height < 16:
        raise ValueError(f"Image {img.width}x{img.height} below 16x16 minimum.")

    orig_size = (img.width, img.height)

    # Convert to grayscale for intensity stats
    gray = img.convert("L")
    arr  = np.array(gray, dtype=np.float32)
    variance = float(np.var(arr))
    if variance < 1.0:
        raise ValueError("MRI slice has zero diagnostic variance (blank/saturated).")
    mean_intensity = float(np.mean(arr))

    # Resize and convert to 3-channel RGB (grayscale replicated)
    resized = gray.resize(TARGET_SIZE, Image.Resampling.BILINEAR)
    rgb     = resized.convert("RGB")     # L → RGB by replication
    rgb_arr = np.array(rgb, dtype=np.float32) / 255.0   # (224, 224, 3)

    # Apply ImageNet normalisation
    mean = np.array(IMAGENET_MEAN, dtype=np.float32)
    std  = np.array(IMAGENET_STD,  dtype=np.float32)
    norm = (rgb_arr - mean) / std          # (224, 224, 3)

    # HWC → CHW for PyTorch
    chw  = norm.transpose(2, 0, 1)         # (3, 224, 224)

    return {
        "original_size":  orig_size,
        "target_size":    TARGET_SIZE,
        "channels":       3,
        "mean_intensity": mean_intensity,
        "variance":       variance,
        "status":         "VALID_SLICE",
        "pixel_tensor":   chw.tolist()     # [3, 224, 224]
    }
'''

with open(os.path.join(OUTPUT_DIR, "preprocess.py"), "w", encoding="utf-8") as f:
    f.write(preprocess_code)
print("Written preprocess.py")

# ── MODEL_CARD.md ─────────────────────────────────────────────────────────────
val_acc  = metrics.get("best_val_acc", "N/A")
test_acc = metrics.get("test_accuracy", "N/A")

card = f"""# Model Card — Brain Tumor MRI DenseNet-121

## Model Details
| Field | Value |
|---|---|
| Name | mri_cnn |
| Architecture | DenseNet-121 (ImageNet pretrained, head replaced) |
| Parameters | ~7M |
| Input | (3, 224, 224) — grayscale MRI slice replicated to 3 channels |
| Output | (4,) softmax probabilities |
| Model version | mri-densenet121-kaggle-v1 |

## Dataset
| Field | Value |
|---|---|
| Dataset | Kaggle Brain Tumor MRI Dataset (masoudnickparvar) |
| Images | ~7,023 total (Training + Testing splits) |
| Classes | glioma, meningioma, notumor, pituitary |
| Split | Pre-defined Training / Testing (no patient IDs) |

## Performance
| Metric | Value |
|---|---|
| Best Val (Test) Accuracy | {val_acc} |
| Final Test Accuracy | {test_acc} |

## Label Mapping
| Index | Kaggle Class | Clinical Label |
|---|---|---|
| 0 | glioma | Glioma / High-Grade Neoplasm |
| 1 | meningioma | Meningioma |
| 2 | notumor | No Tumor Detected |
| 3 | pituitary | Pituitary Adenoma |

## Known Limitations & Bias
- **Source-domain bias**: The `notumor` class images are from a different scanner
  than the tumor classes. Run `domain_bias_report.json` to check brightness shift.
- **No patient IDs**: Cannot guarantee patient-level split; test-set leakage is possible.
- **Dropped classes**: Stroke/hemorrhage not included (no suitable open dataset).
- **Single-slice only**: No volumetric or multi-sequence fusion.
- **Not clinically validated**: Do not use for real clinical decisions.

## SHA-256
`{sha256}`
"""

with open(os.path.join(OUTPUT_DIR, "MODEL_CARD.md"), "w", encoding="utf-8") as f:
    f.write(card)
print("Written MODEL_CARD.md")

print(f"\n✅ Bundle exported to: {OUTPUT_DIR}")
print("Copy the entire output/mri_cnn/ folder to:")
print("  HealthGuardAI/backend/data/imaging/mri_cnn/")
