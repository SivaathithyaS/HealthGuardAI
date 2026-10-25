"""
Brain Tumor MRI Dataset Loader
================================
Kaggle dataset: masoudnickparvar/brain-tumor-mri-dataset

Expected folder layout:
    mri_tumor/data/
        Training/
            glioma/        (826 images)
            meningioma/    (822 images)
            notumor/       (395 images)
            pituitary/     (827 images)
        Testing/
            glioma/        (100 images)
            meningioma/    (115 images)
            notumor/       (105 images)
            pituitary/     (74 images)

Classes (alphabetical, matching torchvision.datasets.ImageFolder convention):
  0 = glioma
  1 = meningioma
  2 = notumor
  3 = pituitary

Source-domain bias check:
  'notumor' images come from a different scanner than the tumor images.
  This script runs a hash-based dedup and computes a class × image-stats
  table so you can check for distributional shifts.
"""
import os
import hashlib
import numpy as np
from PIL import Image
from collections import defaultdict
import torch
from torch.utils.data import Dataset
from torchvision import transforms


CLASS_NAMES = ["glioma", "meningioma", "notumor", "pituitary"]
CLASS_INDEX  = {c: i for i, c in enumerate(CLASS_NAMES)}

# ── Transforms ────────────────────────────────────────────────────────────────
TRAIN_TRANSFORM = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.Grayscale(num_output_channels=3),   # replicate L → RGB
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std =[0.229, 0.224, 0.225])
])

VAL_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std =[0.229, 0.224, 0.225])
])


def _file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def deduplicate_and_scan(data_dir: str) -> dict:
    """
    Scans all images, removes exact duplicates (MD5), and returns per-class
    mean/std brightness statistics to surface source-domain bias.
    """
    print("Running deduplication & domain bias scan…")
    seen_hashes: dict[str, str] = {}
    duplicates   = []
    stats: dict[str, list] = defaultdict(list)

    for split in ("Training", "Testing"):
        split_path = os.path.join(data_dir, split)
        if not os.path.exists(split_path):
            continue
        for cls in CLASS_NAMES:
            cls_path = os.path.join(split_path, cls)
            if not os.path.exists(cls_path):
                continue
            for fname in os.listdir(cls_path):
                fpath = os.path.join(cls_path, fname)
                h = _file_hash(fpath)
                if h in seen_hashes:
                    duplicates.append((fpath, seen_hashes[h]))
                    os.rename(fpath, fpath + ".dup")  # soft-remove dup
                else:
                    seen_hashes[h] = fpath
                    try:
                        img = Image.open(fpath).convert("L")
                        arr = np.array(img, dtype=np.float32)
                        stats[f"{split}/{cls}"].append((arr.mean(), arr.std()))
                    except Exception:
                        pass

    print(f"  Duplicates found and soft-removed: {len(duplicates)}")
    print("\n  Per-class brightness (mean ± std) — look for 'notumor' divergence:")
    report = {}
    for key, vals in stats.items():
        means = [v[0] for v in vals]
        stds  = [v[1] for v in vals]
        report[key] = {
            "n":        len(vals),
            "brightness_mean": float(np.mean(means)),
            "brightness_std":  float(np.mean(stds))
        }
        print(f"  {key:<28}: n={len(vals):4d}  "
              f"brightness={np.mean(means):.1f} ± {np.mean(stds):.1f}")

    print()
    return report


class BrainTumorDataset(Dataset):
    """
    Brain tumor MRI dataset from the Kaggle masoudnickparvar collection.

    Args:
        data_dir : path to Training/ or Testing/ directory
        split    : "Training" or "Testing"
        transform: torchvision transform to apply
    """
    def __init__(self, data_dir: str, split: str, transform=None):
        self.transform = transform
        self.samples   = []

        split_path = os.path.join(data_dir, split)
        for cls in CLASS_NAMES:
            cls_path = os.path.join(split_path, cls)
            if not os.path.exists(cls_path):
                print(f"  WARNING: class folder missing: {cls_path}")
                continue
            label = CLASS_INDEX[cls]
            for fname in sorted(os.listdir(cls_path)):
                if fname.endswith(".dup"):
                    continue  # skip deduplicated files
                fpath = os.path.join(cls_path, fname)
                if os.path.isfile(fpath):
                    self.samples.append((fpath, label))

        print(f"  {split} dataset: {len(self.samples)} images "
              f"({dict(zip(CLASS_NAMES, self._count()))})")

    def _count(self):
        counts = [0] * len(CLASS_NAMES)
        for _, label in self.samples:
            counts[label] += 1
        return counts

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path)
        if self.transform:
            img = self.transform(img)
        return img, torch.tensor(label, dtype=torch.long)


def compute_class_weights(dataset: BrainTumorDataset) -> "torch.Tensor":
    """Inverse-frequency weights for imbalanced MRI classes."""
    counts = np.zeros(len(CLASS_NAMES), dtype=np.float32)
    for _, label in dataset.samples:
        counts[label.item() if hasattr(label, "item") else label] += 1
    weights = counts.sum() / (len(CLASS_NAMES) * counts + 1e-6)
    return torch.tensor(weights, dtype=torch.float32)


if __name__ == "__main__":
    import sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    report = deduplicate_and_scan(data_dir)
    ds = BrainTumorDataset(data_dir, "Training", transform=VAL_TRANSFORM)
    img, label = ds[0]
    print(f"Image tensor shape: {img.shape}, label: {CLASS_NAMES[label.item()]}")
