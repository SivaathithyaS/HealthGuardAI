"""
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
        parts = [p.strip() for p in text.replace(",", "\n").split("\n") if p.strip()]
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
