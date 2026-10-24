# Model Card: HealthGuard MRI-CNN-v1 (Neuro-Oncology & Acute Lesion Classifier)

## Model Details
- **Architecture**: 2D/3D DenseNet-121 CNN architecture trained with Gradient-weighted Class Activation Mapping (Grad-CAM) at the final dense block.
- **Input Modality**: Axial T1-weighted contrast-enhanced (T1-Gd) and T2-FLAIR brain MRI slices, standardized to 224x224 grayscale.
- **Target Conditions**:
  1. No Acute Intra-Axial Abnormality
  2. High-Grade Glioma / Neoplasm (e.g. Glioblastoma Multiforme)
  3. Acute Ischemic Infarct (Cytotoxic Edema)
  4. Intracranial Hemorrhage (Parenchymal / Subarachnoid)
- **Model Version**: `mri-cnn-v1-stub` (Clinical prototype stub)

## Intended Clinical Use
Designed for automated neuroradiology triage, lesion localization, and emergency department workflow prioritization when sudden neurologic deficits or seizures present.

## Limitations & Safeguards
- Definitive diagnosis of high-grade glioma strictly requires stereotactic tissue biopsy and molecular biomarker profiling (IDH1/2 mutation, MGMT methylation, 1p/19q codeletion).
- Severe patient motion artifacts, susceptibility from dental hardware, or prior craniotomy defects can degrade Grad-CAM localization.
- Operating decision threshold is locked at `0.60`. Inconclusive probabilities (< 0.60) automatically assign an `uncertain` classification requiring human neuroradiologist over-read.
