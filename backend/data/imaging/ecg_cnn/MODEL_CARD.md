# Model Card: HealthGuard ECG-CNN-v1 (Lead-II Rhythm Classifier)

## Model Details
- **Architecture**: 1D ResNet-18 variant with temporal convolutional layers, Squeeze-and-Excitation blocks, and 1D Grad-CAM attribution.
- **Input Modality**: Single-lead rhythm strip (Lead II default), 100 Hz sampling rate, 5-second window (500 samples).
- **Target Conditions**:
  1. Normal Sinus Rhythm (NSR)
  2. Atrial Fibrillation / Flutter (AFib)
  3. ST Elevation / Acute Subepicardial Ischemia (STEMI pattern)
  4. Ventricular Tachycardia / Wide-Complex Tachyarrhythmia (VT)
- **Model Version**: `ecg-cnn-v1-stub` (Clinical prototype stub)

## Intended Clinical Use
Designed for automated rhythm triage and ST segment abnormality surveillance in emergency department triage, telemetry monitoring units, and post-procedural recovery.

## Limitations & Safeguards
- Not intended as a standalone diagnostic modality for primary PCI activation without physician review.
- Pacemaker spikes and high-frequency baseline wander may alter saliency scores.
- Clinical threshold is locked at `0.60`. Any prediction with maximum posterior probability < 0.60 triggers automatic `uncertain` status and flags the tracing for urgent manual electrophysiologist over-read.
