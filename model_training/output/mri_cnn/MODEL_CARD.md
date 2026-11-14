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

## Explainability — Real Grad-CAM
Grad-CAM is computed on the last conv layer of DenseBlock4:
`model.features.denseblock4.denselayer16.conv2`

The activation map (7×7) is upsampled to 224×224 with bilinear interpolation,
normalised to [0, 1], and rendered as a jet-colormap overlay on the input slice.
Inplace ReLUs in DenseNet are handled by using `torch.autograd.grad` on the
retained activation tensor (rather than gradient hooks on parameters).

## Known Limitations & Bias
- **Source-domain bias**: The `notumor` class images are from a different scanner
  than the tumor classes. Run `domain_bias_report.json` to check brightness shift.
- **No patient IDs**: Cannot guarantee patient-level split; test-set leakage is possible.
- **Dropped classes**: Stroke/hemorrhage not included (no suitable open dataset).
- **Single-slice only**: No volumetric or multi-sequence fusion.
- **Not clinically validated**: Do not use for real clinical decisions.

## SHA-256
`ee5dae2ca2ef0baab40a6afec5569d295c7fecd6f1f4c68cfddb105b5357e343`
