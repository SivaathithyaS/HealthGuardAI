# Model Card — Brain Tumor MRI DenseNet-121

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
| Best Val (Test) Accuracy | N/A |
| Final Test Accuracy | N/A |

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
`69768b6c01bb617196044b1fdc82781e6afac35456cc78979b3923ca7921b24d`
