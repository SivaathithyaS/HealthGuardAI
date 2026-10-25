"""
ECG 1D-CNN Training Script — PTB-XL v1.0.3
============================================
Run from the ecg_ptbxl/ directory:
    python train_ecg.py

Outputs:
    checkpoints/best_ecg_model.pt   ← best validation checkpoint
    training_curves.png
    confusion_matrix.png

After this finishes, run:
    python export_bundle.py
"""
import os
import time
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from model   import ECGResNet1D
from dataset import PTBXLDataset, compute_class_weights, SUPERCLASS_LABELS

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR    = "data"          # folder containing ptbxl_database.csv + records100/
CKPT_DIR    = "checkpoints"
BATCH_SIZE  = 128
LR          = 3e-4
EPOCHS      = 50
PATIENCE    = 8               # early stopping patience (val epochs without improvement)
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"

TRAIN_FOLDS = list(range(1, 9))   # folds 1-8
VAL_FOLDS   = [9]
TEST_FOLDS  = [10]                 # held-out, used only in final evaluation

# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(CKPT_DIR, exist_ok=True)

print(f"Device : {DEVICE}")
print(f"Labels : {SUPERCLASS_LABELS}")


# ── Datasets & Loaders ───────────────────────────────────────────────────────
print("\nLoading train/val datasets (this may take a few minutes)…")
train_ds = PTBXLDataset(DATA_DIR, folds=TRAIN_FOLDS, cache=True)
val_ds   = PTBXLDataset(DATA_DIR, folds=VAL_FOLDS,   cache=True)

print(f"  Train: {len(train_ds)} records")
print(f"  Val  : {len(val_ds)} records")

class_weights = compute_class_weights(train_ds).to(DEVICE)
print(f"  Class weights: {class_weights.cpu().numpy().round(3)}")

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=4, pin_memory=True)


# ── Model, Optimizer, Scheduler ──────────────────────────────────────────────
model = ECGResNet1D(num_classes=len(SUPERCLASS_LABELS)).to(DEVICE)
total_params = sum(p.numel() for p in model.parameters())
print(f"\nModel parameters: {total_params:,}")

criterion  = nn.CrossEntropyLoss(weight=class_weights)
optimizer  = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)


# ── Training Loop ─────────────────────────────────────────────────────────────
def run_epoch(loader, train: bool):
    model.train() if train else model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(train):
        for x, y in loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            logits = model(x)
            loss   = criterion(logits, y)
            if train:
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            total_loss += loss.item() * len(y)
            correct    += (logits.argmax(1) == y).sum().item()
            total      += len(y)
    return total_loss / total, correct / total


best_val_acc    = 0.0
epochs_no_improv = 0
train_losses, val_losses = [], []
train_accs,   val_accs   = [], []

print(f"\nTraining for up to {EPOCHS} epochs (early stop patience={PATIENCE})…\n")

for epoch in range(1, EPOCHS + 1):
    t0 = time.time()
    tr_loss, tr_acc = run_epoch(train_loader, train=True)
    vl_loss, vl_acc = run_epoch(val_loader,   train=False)
    scheduler.step()

    train_losses.append(tr_loss); val_losses.append(vl_loss)
    train_accs.append(tr_acc);     val_accs.append(vl_acc)

    elapsed = time.time() - t0
    print(f"Epoch {epoch:02d}/{EPOCHS} | "
          f"train loss={tr_loss:.4f} acc={tr_acc:.4f} | "
          f"val loss={vl_loss:.4f} acc={vl_acc:.4f} | "
          f"lr={scheduler.get_last_lr()[0]:.2e} | {elapsed:.1f}s")

    if vl_acc > best_val_acc:
        best_val_acc = vl_acc
        torch.save(model, os.path.join(CKPT_DIR, "best_ecg_model.pt"))
        print(f"  ✓ New best val acc: {best_val_acc:.4f} — checkpoint saved")
        epochs_no_improv = 0
    else:
        epochs_no_improv += 1
        if epochs_no_improv >= PATIENCE:
            print(f"\nEarly stopping after {epoch} epochs (no improvement for {PATIENCE} epochs).")
            break


# ── Final Evaluation on Test Fold ─────────────────────────────────────────────
print("\nEvaluating on held-out test fold (strat_fold=10)…")
model = torch.load(os.path.join(CKPT_DIR, "best_ecg_model.pt"), map_location=DEVICE)
model.eval()

test_ds     = PTBXLDataset(DATA_DIR, folds=TEST_FOLDS, cache=True)
test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

all_preds, all_labels, all_probs = [], [], []
with torch.no_grad():
    for x, y in test_loader:
        x = x.to(DEVICE)
        logits = model(x)
        probs  = torch.softmax(logits, dim=1).cpu().numpy()
        preds  = logits.argmax(1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(y.numpy())
        all_probs.extend(probs)

all_preds  = np.array(all_preds)
all_labels = np.array(all_labels)
all_probs  = np.array(all_probs)

print("\nClassification Report:")
print(classification_report(all_labels, all_preds, target_names=SUPERCLASS_LABELS))

# Per-class AUC
try:
    from sklearn.preprocessing import label_binarize
    y_bin = label_binarize(all_labels, classes=list(range(len(SUPERCLASS_LABELS))))
    auc_scores = {}
    for i, cls in enumerate(SUPERCLASS_LABELS):
        auc_scores[cls] = float(roc_auc_score(y_bin[:, i], all_probs[:, i]))
    print("\nPer-class ROC-AUC:")
    for cls, auc in auc_scores.items():
        print(f"  {cls}: {auc:.4f}")
except Exception as e:
    auc_scores = {}
    print(f"  AUC computation failed: {e}")


# ── Save Training Curves ──────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(train_losses, label="train"); ax1.plot(val_losses, label="val")
ax1.set_title("Loss"); ax1.legend(); ax1.set_xlabel("Epoch")
ax2.plot(train_accs, label="train"); ax2.plot(val_accs, label="val")
ax2.set_title("Accuracy"); ax2.legend(); ax2.set_xlabel("Epoch")
fig.tight_layout()
fig.savefig("training_curves.png", dpi=120)
print("\nSaved training_curves.png")

cm = confusion_matrix(all_labels, all_preds)
fig2, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=SUPERCLASS_LABELS,
            yticklabels=SUPERCLASS_LABELS, cmap="Blues", ax=ax)
ax.set_xlabel("Predicted"); ax.set_ylabel("True")
ax.set_title("Test Set Confusion Matrix — ECG PTB-XL")
fig2.tight_layout()
fig2.savefig("confusion_matrix.png", dpi=120)
print("Saved confusion_matrix.png")

# Save eval metrics for export_bundle.py to read
metrics = {
    "best_val_acc": best_val_acc,
    "test_accuracy": float((all_preds == all_labels).mean()),
    "auc_per_class": auc_scores
}
with open(os.path.join(CKPT_DIR, "eval_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2)

print("\n✅ Training complete. Run  python export_bundle.py  next.")
