# Model Card — ECG 1D-CNN (PTB-XL)

## Model Details
| Field | Value |
|---|---|
| Name | ecg_cnn |
| Architecture | 1D ResNet (4 residual stages, 256 channels in final stage) |
| Parameters | ~0.9M |
| Input | (1, 500) — Lead II, 500 samples (10 s at 100 Hz decimated 2:1) |
| Output | (5,) softmax probabilities |
| Model version | ecg-resnet1d-ptbxl-v1 |

## Preprocessing
| Step | Description |
|---|---|
| Accepted input | 1000 samples at 100 Hz (10 s) **or** 5000 samples at 500 Hz (10 s) |
| Decimation | `scipy.signal.resample_poly(sig, 1, 2)` → 500 samples (matches training) |
| 500 Hz path | `resample_poly(sig, 1, 10)` → 1000, then `resample_poly(sig, 1, 2)` → 500 |
| Normalisation | Z-score per-record (no band-pass filter) |
| Rejection | Any other sample count raises `ValueError` with a clear message |

> [!IMPORTANT]
> Training uses the PTB-XL 100 Hz records (1000 samples for 10 s), decimated
> to 500 with `resample_poly(sig, 1, 2)`.  The backend preprocess.py mirrors
> this exactly.  Earlier versions incorrectly described the input as "5 s at
> 100 Hz"; the correct description is **10 s at 100 Hz decimated to 500 samples**.

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
| Best Val Accuracy | 0.6364 |
| Test Accuracy | 0.6278 |

### Per-class ROC-AUC
| Class | AUC |
|---|---|
| NORM | 0.8889 |
| MI | 0.7798 |
| STTC | 0.8453 |
| CD | 0.8061 |
| HYP | 0.6721 |

## Label Mapping
| Index | Short | Full Label |
|---|---|---|
| 0 | NORM | Normal Sinus Rhythm |
| 1 | MI   | Myocardial Infarction |
| 2 | STTC | ST/T-Wave Change |
| 3 | CD   | Conduction Disturbance |
| 4 | HYP  | Cardiac Hypertrophy |

## Explainability
Real 1D Grad-CAM is computed on `layer4.1.conv2` (last Conv1d layer).
Activation maps are upsampled back to 500 samples and normalised to [0, 1].

## Limitations
- Trained on Lead II only (12-lead data available but not used here)
- No Ventricular Tachycardia class (not reliably annotated in PTB-XL)
- Do not use for real clinical decisions without further validation
- Single-label assignment per record (PTB-XL is multi-label by nature)

## SHA-256
`bb51d7f2457c27347599e1ff8f5cf4cfc9027577f73232fde2ea36b7e2083a78`
