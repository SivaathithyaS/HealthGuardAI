# HealthGuard AI — Model Training Workspace
# ==========================================
# GPU training scripts for ECG and MRI CNN models.
# Run these on a machine with CUDA GPU.
#
# FOLDER STRUCTURE (after you download and place datasets):
#
# model_training/
# ├── README_TRAINING.md           ← this file
# ├── requirements_train.txt       ← pip install this first
# ├── ecg_ptbxl/
# │   ├── data/                    ← place PTB-XL dataset here
# │   │   ├── records100/          (from physionet.org download)
# │   │   ├── ptbxl_database.csv
# │   │   └── scp_statements.csv
# │   ├── train_ecg.py             ← main training script
# │   ├── model.py                 ← 1D-CNN ResNet architecture
# │   ├── dataset.py               ← PTB-XL dataloader
# │   └── export_bundle.py         ← exports weights.pt + config.json
# ├── mri_tumor/
# │   ├── data/                    ← place Kaggle dataset here
# │   │   ├── Training/
# │   │   │   ├── glioma/
# │   │   │   ├── meningioma/
# │   │   │   ├── notumor/
# │   │   │   └── pituitary/
# │   │   └── Testing/
# │   │       ├── glioma/
# │   │       ├── meningioma/
# │   │       ├── notumor/
# │   │       └── pituitary/
# │   ├── train_mri.py             ← main training script
# │   ├── model.py                 ← DenseNet-121 fine-tune
# │   ├── dataset.py               ← MRI dataloader + dedup check
# │   └── export_bundle.py         ← exports weights.pt + config.json
# └── output/
#     ├── ecg_cnn/                 ← trained bundle (copy to HealthGuardAI)
#     └── mri_cnn/                 ← trained bundle (copy to HealthGuardAI)
#
# ══════════════════════════════════════════════════════════════
# DATASET DOWNLOAD LINKS
# ══════════════════════════════════════════════════════════════
#
# ── ECG: PTB-XL v1.0.3 ──────────────────────────────────────
# URL: https://physionet.org/content/ptb-xl/1.0.3/
# No login needed (open access).
# Download "ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3.zip"
# Unzip and place the contents inside:  model_training/ecg_ptbxl/data/
# Expected after unzip:
#   model_training/ecg_ptbxl/data/records100/00000/00001_lr.dat ...
#   model_training/ecg_ptbxl/data/ptbxl_database.csv
#   model_training/ecg_ptbxl/data/scp_statements.csv
#
# ── MRI: Brain Tumor MRI Dataset ─────────────────────────────
# URL: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
# Requires Kaggle account. Log in → go to the link above → click Download.
# Unzip and place the contents inside:  model_training/mri_tumor/data/
# Expected after unzip:
#   model_training/mri_tumor/data/Training/glioma/   (826 images)
#   model_training/mri_tumor/data/Training/meningioma/ (822 images)
#   model_training/mri_tumor/data/Training/notumor/  (395 images)
#   model_training/mri_tumor/data/Training/pituitary/ (827 images)
#   model_training/mri_tumor/data/Testing/glioma/    (100 images)
#   ... etc
#
# ══════════════════════════════════════════════════════════════
# STEPS TO TRAIN
# ══════════════════════════════════════════════════════════════
#
# 1. Install dependencies (once):
#    pip install -r requirements_train.txt
#
# 2. Train ECG model (~30–60 min on a single GPU):
#    cd ecg_ptbxl
#    python train_ecg.py
#    python export_bundle.py
#
# 3. Train MRI model (~20–40 min on a single GPU):
#    cd ../mri_tumor
#    python train_mri.py
#    python export_bundle.py
#
# 4. Copy output bundles to HealthGuardAI:
#    Copy  output/ecg_cnn/  →  backend/data/imaging/ecg_cnn/
#    Copy  output/mri_cnn/  →  backend/data/imaging/mri_cnn/
#    (overwrite weights.pt and config.json; keep the new preprocess.py)
#
# ══════════════════════════════════════════════════════════════
# WHAT THE EXPORT SCRIPTS PRODUCE
# ══════════════════════════════════════════════════════════════
#
# output/ecg_cnn/
#   weights.pt       ← full model (architecture + state_dict via torch.save(model))
#   config.json      ← labels, threshold, sha256, stub=false
#   preprocess.py    ← updated (12-lead → Lead II slice, resample to 500 pts)
#   MODEL_CARD.md    ← training metadata, AUC per class
#
# output/mri_cnn/
#   weights.pt       ← DenseNet-121 fine-tuned (torch.save(model))
#   config.json      ← 4 tumor classes, sha256, stub=false
#   preprocess.py    ← unchanged from stub (224×224 grayscale → RGB for DenseNet)
#   MODEL_CARD.md    ← training metadata, per-class accuracy
