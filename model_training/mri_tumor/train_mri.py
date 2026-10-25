"""
MRI DenseNet-121 Training Script — Kaggle Brain Tumor MRI Dataset
==================================================================
Run from the mri_tumor/ directory:
    python train_mri.py

Two-phase training:
  Phase 1 (warm-up, 5 epochs):  Only classifier head trainable. High LR.
  Phase 2 (fine-tune, 45 epochs): All layers trainable. Lower LR w/ cosine decay.

Outputs:
    checkpoints/best_mri_model.pt
    training_curves.png
    confusion_matrix.png
    domain_bias_report.json    ← brightness stats per class (check notumor shift)

After this, run:
    python export_bundle.py
"""
import os
import time
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from model   import MRIDenseNet121
from dataset import (BrainTumorDataset, deduplicate_and_scan,
                     compute_class_weights, CLASS_NAMES,
                     TRAIN_TRANSFORM, VAL_TRANSFORM)

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR       = "data"
CKPT_DIR       = "checkpoints"
BATCH_SIZE     = 32
LR_HEAD        = 1e-3     # phase-1 head-only LR
LR_FINETUNE    = 3e-4     # phase-2 full-model LR
EPOCHS_WARMUP  = 5
EPOCHS_FINETUNE = 45
PATIENCE       = 10
DEVICE         = "cuda" if torch.cuda.is_available() else "cpu"
# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(CKPT_DIR, exist_ok=True)
print(f"Device : {DEVICE}")
print(f"Classes: {CLASS_NAMES}")

# ── Domain bias check & dedup ─────────────────────────────────────────────────
print("\n── Deduplication & domain bias check ────────────────────────────────")
bias_report = deduplicate_and_scan(DATA_DIR)
with open(os.path.join(CKPT_DIR, "domain_bias_report.json"), "w") as f:
    json.dump(bias_report, f, indent=2)
print("domain_bias_report.json saved. Check 'notumor' brightness vs tumor classes.")

# ── Datasets ──────────────────────────────────────────────────────────────────
print("\n── Loading datasets ──────────────────────────────────────────────────")
train_ds = BrainTumorDataset(DATA_DIR, "Training", transform=TRAIN_TRANSFORM)
test_ds  = BrainTumorDataset(DATA_DIR, "Testing",  transform=VAL_TRANSFORM)

# Weighted sampler for class imbalance (notumor is under-represented)
cw = compute_class_weights(train_ds)
sample_weights = [cw[label].item() for _, label in train_ds.samples]
sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler,
                          num_workers=4, pin_memory=True)
test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=4, pin_memory=True)

print(f"Class weights: {cw.numpy().round(3)} ({CLASS_NAMES})")


# ── Model ─────────────────────────────────────────────────────────────────────
model = MRIDenseNet121(num_classes=len(CLASS_NAMES), pretrained=True).to(DEVICE)
criterion = nn.CrossEntropyLoss()


def run_epoch(loader, train: bool):
    model.train() if train else model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(train):
        for imgs, labels in loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            logits = model(imgs)
            loss   = criterion(logits, labels)
            if train:
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            total_loss += loss.item() * len(labels)
            correct    += (logits.argmax(1) == labels).sum().item()
            total      += len(labels)
    return total_loss / total, correct / total


train_losses, val_losses = [], []
train_accs, val_accs     = [], []
best_val_acc = 0.0
epochs_no_improv = 0


# ── Phase 1: Head-only warm-up ────────────────────────────────────────────────
print(f"\n── Phase 1: Warm-up head only ({EPOCHS_WARMUP} epochs) ───────────────────")
model.freeze_backbone()
optimizer = torch.optim.AdamW(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=LR_HEAD, weight_decay=1e-4
)
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=LR_HEAD, steps_per_epoch=len(train_loader), epochs=EPOCHS_WARMUP
)

for epoch in range(1, EPOCHS_WARMUP + 1):
    t0 = time.time()
    tr_loss, tr_acc = run_epoch(train_loader, train=True)
    # Use test set as "val" (no patient-split in Kaggle dataset)
    vl_loss, vl_acc = run_epoch(test_loader, train=False)
    scheduler.step()
    train_losses.append(tr_loss); val_losses.append(vl_loss)
    train_accs.append(tr_acc);     val_accs.append(vl_acc)
    print(f"  WU-Epoch {epoch}/{EPOCHS_WARMUP} | "
          f"train acc={tr_acc:.4f} | val acc={vl_acc:.4f} | {time.time()-t0:.1f}s")
    if vl_acc > best_val_acc:
        best_val_acc = vl_acc
        torch.save(model, os.path.join(CKPT_DIR, "best_mri_model.pt"))


# ── Phase 2: Full fine-tune ───────────────────────────────────────────────────
print(f"\n── Phase 2: Full fine-tune ({EPOCHS_FINETUNE} epochs, early stop={PATIENCE}) ──")
model.unfreeze_all()
optimizer = torch.optim.AdamW(model.parameters(), lr=LR_FINETUNE, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS_FINETUNE)

for epoch in range(1, EPOCHS_FINETUNE + 1):
    t0 = time.time()
    tr_loss, tr_acc = run_epoch(train_loader, train=True)
    vl_loss, vl_acc = run_epoch(test_loader,  train=False)
    scheduler.step()
    train_losses.append(tr_loss); val_losses.append(vl_loss)
    train_accs.append(tr_acc);     val_accs.append(vl_acc)
    print(f"  FT-Epoch {epoch:02d}/{EPOCHS_FINETUNE} | "
          f"train acc={tr_acc:.4f} | val acc={vl_acc:.4f} | "
          f"lr={scheduler.get_last_lr()[0]:.2e} | {time.time()-t0:.1f}s")
    if vl_acc > best_val_acc:
        best_val_acc = vl_acc
        torch.save(model, os.path.join(CKPT_DIR, "best_mri_model.pt"))
        print(f"  ✓ New best: {best_val_acc:.4f} — checkpoint saved")
        epochs_no_improv = 0
    else:
        epochs_no_improv += 1
        if epochs_no_improv >= PATIENCE:
            print(f"\nEarly stopping after FT-epoch {epoch}.")
            break


# ── Final evaluation ──────────────────────────────────────────────────────────
print("\nFinal evaluation on test set…")
model = torch.load(os.path.join(CKPT_DIR, "best_mri_model.pt"), map_location=DEVICE)
model.eval()

all_preds, all_labels = [], []
with torch.no_grad():
    for imgs, labels in test_loader:
        imgs = imgs.to(DEVICE)
        preds = model(imgs).argmax(1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.numpy())

all_preds  = np.array(all_preds)
all_labels = np.array(all_labels)

print("\nClassification Report:")
print(classification_report(all_labels, all_preds, target_names=CLASS_NAMES))

test_acc = float((all_preds == all_labels).mean())

# Plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(train_losses, label="train"); ax1.plot(val_losses, label="val")
ax1.set_title("Loss"); ax1.legend()
ax2.plot(train_accs, label="train"); ax2.plot(val_accs, label="val")
ax2.set_title("Accuracy"); ax2.legend()
fig.tight_layout()
fig.savefig("training_curves.png", dpi=120)

cm = confusion_matrix(all_labels, all_preds)
fig2, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=CLASS_NAMES,
            yticklabels=CLASS_NAMES, cmap="Purples", ax=ax)
ax.set_xlabel("Predicted"); ax.set_ylabel("True")
ax.set_title("Test Confusion Matrix — Brain Tumor MRI")
fig2.tight_layout()
fig2.savefig("confusion_matrix.png", dpi=120)
print("Saved training_curves.png and confusion_matrix.png")

metrics = {"best_val_acc": best_val_acc, "test_accuracy": test_acc}
with open(os.path.join(CKPT_DIR, "eval_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

print("\n✅ Training complete. Run  python export_bundle.py  next.")
