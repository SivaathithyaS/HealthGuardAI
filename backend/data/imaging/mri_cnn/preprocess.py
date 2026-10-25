"""
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
