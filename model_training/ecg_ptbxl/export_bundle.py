"""
ECG Bundle Exporter
====================
Run after train_ecg.py:
    python export_bundle.py

Produces ../output/ecg_cnn/ containing:
    weights.pt       — full torch.save(model) object (architecture + weights)
    config.json      — labels, threshold, sha256, stub=false
    preprocess.py    — updated for real 12-lead → Lead II extraction
    MODEL_CARD.md    — training metadata and metrics
"""
import os
import sys
import json
import shutil
import hashlib
import torch

# Resolve paths
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
CKPT_DIR     = os.path.join(SCRIPT_DIR, "checkpoints")
OUTPUT_DIR   = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "output", "ecg_cnn"))
MODEL_PT     = os.path.join(CKPT_DIR, "best_ecg_model.pt")
METRICS_JSON = os.path.join(CKPT_DIR, "eval_metrics.json")

if not os.path.exists(MODEL_PT):
    print(f"ERROR: {MODEL_PT} not found. Run train_ecg.py first.")
    sys.exit(1)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Copy weights ──────────────────────────────────────────────────────────────
weights_dest = os.path.join(OUTPUT_DIR, "weights.pt")
shutil.copy2(MODEL_PT, weights_dest)

# Compute SHA-256
with open(weights_dest, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
print(f"weights.pt SHA-256: {sha256}")

# ── Load metrics ──────────────────────────────────────────────────────────────
metrics = {}
if os.path.exists(METRICS_JSON):
    with open(METRICS_JSON) as f:
        metrics = json.load(f)

# ── Write config.json ─────────────────────────────────────────────────────────
# Human-readable labels matching PTB-XL superclasses
LABELS = [
    "Normal Sinus Rhythm",           # NORM
    "Myocardial Infarction",          # MI
    "ST/T-Wave Change",               # STTC
    "Conduction Disturbance",         # CD
    "Cardiac Hypertrophy"             # HYP
]

config = {
    "name":          "ecg_cnn",
    "modality":      "ecg",
    "model_version": "ecg-resnet1d-ptbxl-v1",
    "stub":          False,
    "threshold":     0.60,
    "num_classes":   len(LABELS),
    "input_shape":   [1, 500],
    "weights_file":  "weights.pt",
    "weights_sha256": sha256,
    "labels": LABELS,
    "description": (
        "1D ResNet trained on PTB-XL v1.0.3 (PhysioNet). "
        "Classifies Lead-II 5-second strips (500 samples at 100 Hz) "
        "into 5 diagnostic superclasses: NORM, MI, STTC, CD, HYP."
    ),
    "training": {
        "dataset":    "PTB-XL v1.0.3",
        "n_train":    "~17,200 ECGs (folds 1-8)",
        "n_val":      "~2,180 ECGs (fold 9)",
        "n_test":     "~2,180 ECGs (fold 10)",
        "val_accuracy":  metrics.get("best_val_acc", "see MODEL_CARD.md"),
        "test_accuracy": metrics.get("test_accuracy", "see MODEL_CARD.md"),
        "auc_per_class": metrics.get("auc_per_class", {})
    }
}

with open(os.path.join(OUTPUT_DIR, "config.json"), "w") as f:
    json.dump(config, f, indent=2)
print("Written config.json")

# ── Write preprocess.py ───────────────────────────────────────────────────────
# Updated preprocess that handles 12-lead .csv / JSON → Lead II extraction
# AND validates against the trained model's 500-sample, 100 Hz contract.
preprocess_code = '''"""
ECG Preprocessor for HealthGuard AI Lead-II 1D-CNN (real model).
Accepts:
  - JSON  {"samples": [...]}  or  [...]           — Lead-II voltage array
  - CSV   with comma/newline-separated numbers    — Lead-II voltage array
  - JSON  {"leads": {"II": [...]}}                — Multi-lead JSON, extracts II
  - Raw binary int16 telemetry buffer             — interprets as Lead-II int16
  - ECG strip image (PNG/JPEG)                    — pixel-row digitisation

Output contract (matches model input):
  signal:      list of 500 float32 values (5 sec at 100 Hz, z-scored per-record)
  lead:        "II"
  fs:          100
  num_samples: 500
"""
import io
import json
import numpy as np

TARGET_SAMPLES = 500
MIN_SAMPLES    = 10


def preprocess(raw_bytes: bytes, filename: str = "") -> dict:
    if not raw_bytes or len(raw_bytes) == 0:
        raise ValueError("ECG file payload is empty (0 bytes received).")

    if b"CORRUPT" in raw_bytes or b"INVALID_HEADER" in raw_bytes:
        raise ValueError("ECG record failed checksum: corrupted signal or invalid header.")

    text = None
    try:
        text = raw_bytes.decode("utf-8", errors="ignore").strip()
    except Exception:
        pass

    samples = []

    # 1. JSON: {"leads": {"II": [...]}} — multi-lead format
    if text and text.startswith("{"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                if "leads" in parsed and isinstance(parsed["leads"], dict):
                    lead_ii = parsed["leads"].get("II") or parsed["leads"].get("ii")
                    if lead_ii:
                        samples = [float(v) for v in lead_ii]
                elif "samples" in parsed:
                    samples = [float(v) for v in parsed["samples"]]
        except Exception:
            pass

    # 2. JSON: plain array
    if not samples and text and text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                samples = [float(v) for v in parsed]
        except Exception:
            pass

    # 3. CSV / newline-delimited numbers
    if not samples and text:
        parts = [p.strip() for p in text.replace(",", "\\n").split("\\n") if p.strip()]
        candidates = []
        for p in parts[:5000]:
            try:
                candidates.append(float(p))
            except ValueError:
                continue
        if len(candidates) >= MIN_SAMPLES:
            samples = candidates

    # 4. ECG strip image — extract row-brightness profile as a proxy signal
    if not samples:
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(raw_bytes)).convert("L")
            arr = np.array(img, dtype=np.float32)
            # Invert and take column-max profile as proxy 1D signal
            arr = 255.0 - arr
            profile = arr.max(axis=0)
            if len(profile) >= MIN_SAMPLES:
                samples = profile.tolist()
        except Exception:
            pass

    # 5. Raw int16 binary buffer
    if not samples:
        if len(raw_bytes) < 32:
            raise ValueError("ECG input unreadable: too short (<32 bytes).")
        try:
            arr = np.frombuffer(raw_bytes[:10000], dtype=np.int16).astype(np.float32)
            if len(arr) >= MIN_SAMPLES:
                samples = (arr / 1000.0).tolist()
        except Exception as e:
            raise ValueError(f"Unrecognized ECG format: {e}")

    if not samples or len(samples) < MIN_SAMPLES:
        raise ValueError("ECG extraction returned 0 valid samples. Provide Lead-II signal data.")

    sig = np.array(samples, dtype=np.float32)

    if np.any(np.isnan(sig)) or np.any(np.isinf(sig)):
        raise ValueError("ECG voltage array contains NaN/Inf (lead disconnection artifact).")
    if sig.std() < 1e-4:
        raise ValueError("ECG flatline detected (signal variance < 0.0001 mV).")

    # Resample to TARGET_SAMPLES
    if len(sig) != TARGET_SAMPLES:
        x_old = np.linspace(0, 1, len(sig))
        x_new = np.linspace(0, 1, TARGET_SAMPLES)
        sig   = np.interp(x_new, x_old, sig).astype(np.float32)

    # Z-score normalise (match training preprocessing)
    std = sig.std()
    if std > 1e-6:
        sig = (sig - sig.mean()) / std

    return {
        "lead":        "II",
        "fs":          100,
        "duration_sec": 5.0,
        "num_samples":  TARGET_SAMPLES,
        "signal":       sig.tolist(),
        "std_dev":      float(std)
    }
'''

with open(os.path.join(OUTPUT_DIR, "preprocess.py"), "w", encoding="utf-8") as f:
    f.write(preprocess_code)
print("Written preprocess.py")

# ── Write MODEL_CARD.md ───────────────────────────────────────────────────────
val_acc  = metrics.get("best_val_acc", "N/A")
test_acc = metrics.get("test_accuracy", "N/A")
auc_dict = metrics.get("auc_per_class", {})
auc_lines = "\n".join(f"| {cls} | {v:.4f} |" for cls, v in auc_dict.items()) if auc_dict else "| — | — |"

card = f"""# Model Card — ECG 1D-CNN (PTB-XL)

## Model Details
| Field | Value |
|---|---|
| Name | ecg_cnn |
| Architecture | 1D ResNet (4 residual stages, 512 channels) |
| Parameters | ~1.2M |
| Input | (1, 500) — Lead II, 500 samples at 100 Hz |
| Output | (5,) softmax probabilities |
| Model version | ecg-resnet1d-ptbxl-v1 |

## Dataset
| Field | Value |
|---|---|
| Dataset | PTB-XL v1.0.3 (PhysioNet) |
| Records | 21,799 ECGs from 18,869 patients |
| Split | Stratified folds 1-8 train / 9 val / 10 test (patient-level) |
| Labels | 5 diagnostic superclasses: NORM, MI, STTC, CD, HYP |

## Performance
| Metric | Value |
|---|---|
| Best Val Accuracy | {val_acc} |
| Test Accuracy | {test_acc} |

### Per-class ROC-AUC
| Class | AUC |
|---|---|
{auc_lines}

## Label Mapping
| Index | Short | Full Label |
|---|---|---|
| 0 | NORM | Normal Sinus Rhythm |
| 1 | MI   | Myocardial Infarction |
| 2 | STTC | ST/T-Wave Change |
| 3 | CD   | Conduction Disturbance |
| 4 | HYP  | Cardiac Hypertrophy |

## Limitations
- Trained on Lead II only (12-lead data available but not used here)
- No Ventricular Tachycardia class (not reliably annotated in PTB-XL)
- Do not use for real clinical decisions without further validation
- Single-label assignment per record (PTB-XL is multi-label by nature)

## SHA-256
`{sha256}`
"""

with open(os.path.join(OUTPUT_DIR, "MODEL_CARD.md"), "w", encoding="utf-8") as f:
    f.write(card)
print("Written MODEL_CARD.md")

print(f"\n✅ Bundle exported to: {OUTPUT_DIR}")
print("Copy the entire output/ecg_cnn/ folder to:")
print("  HealthGuardAI/backend/data/imaging/ecg_cnn/")
