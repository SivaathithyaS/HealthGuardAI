# Model Card — ECG 1D-CNN (PTB-XL)

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
| Best Val Accuracy | 0.6363636363636364 |
| Test Accuracy | 0.627831715210356 |

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

## Limitations
- Trained on Lead II only (12-lead data available but not used here)
- No Ventricular Tachycardia class (not reliably annotated in PTB-XL)
- Do not use for real clinical decisions without further validation
- Single-label assignment per record (PTB-XL is multi-label by nature)

## SHA-256
`d14463500150900fe2776c4eb9f70f6fdbf7556d2f27b92ed7b26026ab4cdfb7`
