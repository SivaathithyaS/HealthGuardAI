"""
PTB-XL ECG Dataset Loader
===========================
Loads the PTB-XL PhysioNet dataset.

Expected folder layout:
    ecg_ptbxl/data/
        ptbxl_database.csv      (one row per record)
        scp_statements.csv      (SCP code → superclass mapping)
        records100/             (100 Hz .dat/.hea pairs)
            00000/
                00001_lr.dat
                00001_lr.hea
                ...

Reference: https://physionet.org/content/ptb-xl/1.0.3/
strat_fold 10 is reserved for testing; folds 1–8 for train, 9 for val.
"""
import os
import ast
import numpy as np
import pandas as pd
import wfdb
from scipy.signal import resample_poly
from torch.utils.data import Dataset

# PTB-XL superclass mapping (rhythm/morphology SCP codes → our 5 labels)
SUPERCLASS_LABELS = ["NORM", "MI", "STTC", "CD", "HYP"]
SUPERCLASS_INDEX  = {sc: i for i, sc in enumerate(SUPERCLASS_LABELS)}

LEAD_II_INDEX = 1   # Lead order in PTB-XL: I, II, III, aVR, aVL, aVF, V1-V6
TARGET_FS     = 100  # Hz — match the preprocess.py 100 Hz contract
TARGET_SAMPLES = 500 # = 5 seconds × 100 Hz


def load_scp_to_superclass(data_dir: str) -> dict:
    """Returns {scp_code: superclass_string} for codes that have a unique superclass."""
    scp_df = pd.read_csv(os.path.join(data_dir, "scp_statements.csv"), index_col=0)
    scp_map = {}
    for code, row in scp_df.iterrows():
        sc = str(row.get("diagnostic_class", "")).strip()
        if sc in SUPERCLASS_INDEX:
            scp_map[code] = sc
    return scp_map


def aggregate_label(scp_dict: dict, scp_map: dict) -> int | None:
    """
    Given a record's scp_codes dict {code: likelihood}, returns the integer
    superclass index by majority (highest-likelihood mapped superclass).
    Returns None if no diagnostic superclass is mapped.
    """
    votes: dict[str, float] = {}
    for code, likelihood in scp_dict.items():
        sc = scp_map.get(code)
        if sc:
            votes[sc] = votes.get(sc, 0.0) + float(likelihood)
    if not votes:
        return None
    winner = max(votes, key=votes.__getitem__)
    return SUPERCLASS_INDEX[winner]


def load_record_lead_ii(record_path: str, source_fs: int = 100) -> np.ndarray | None:
    """
    Reads one PTB-XL record, extracts Lead II, resamples to TARGET_SAMPLES.
    Returns float32 array of shape (TARGET_SAMPLES,) or None on error.
    """
    try:
        record = wfdb.rdrecord(record_path)
        sig = record.p_signal[:, LEAD_II_INDEX].astype(np.float32)  # (N,)

        # Replace NaN with 0
        sig = np.nan_to_num(sig, nan=0.0)

        # Resample if needed (PTB-XL 100Hz records → 500 samples for 5 sec)
        if len(sig) != TARGET_SAMPLES:
            from math import gcd
            g = gcd(TARGET_SAMPLES, len(sig))
            sig = resample_poly(sig, TARGET_SAMPLES // g, len(sig) // g).astype(np.float32)
            sig = sig[:TARGET_SAMPLES]

        # Z-score normalise per-record
        std = sig.std()
        if std > 1e-6:
            sig = (sig - sig.mean()) / std

        return sig
    except Exception:
        return None


class PTBXLDataset(Dataset):
    """
    PTB-XL single-label dataset using strat_fold stratified splits.

    Args:
        data_dir : path containing ptbxl_database.csv + records100/
        folds    : list of fold integers to include (1-10)
        cache    : if True, preloads all waveforms into RAM (~300 MB for full set)
    """
    def __init__(self, data_dir: str, folds: list[int], cache: bool = True):
        self.data_dir = data_dir
        self.cache    = cache

        # Load metadata
        meta = pd.read_csv(os.path.join(data_dir, "ptbxl_database.csv"), index_col="ecg_id")
        meta["scp_codes"] = meta["scp_codes"].apply(ast.literal_eval)

        # Build SCP → superclass map
        scp_map = load_scp_to_superclass(data_dir)

        # Filter to requested folds and labellable records
        records = []
        for ecg_id, row in meta.iterrows():
            if int(row["strat_fold"]) not in folds:
                continue
            label = aggregate_label(row["scp_codes"], scp_map)
            if label is None:
                continue
            # PTB-XL 100Hz record paths
            rel_path = row["filename_lr"]   # e.g. "records100/00000/00001_lr"
            abs_path = os.path.join(data_dir, rel_path)
            records.append((abs_path, label))

        self.records = records
        self._cache: dict[int, np.ndarray] = {}

        if cache:
            self._preload()

    def _preload(self):
        from tqdm import tqdm
        print(f"  Preloading {len(self.records)} ECG records into RAM…")
        for i, (path, _) in enumerate(tqdm(self.records)):
            sig = load_record_lead_ii(path)
            if sig is not None:
                self._cache[i] = sig

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        import torch
        path, label = self.records[idx]
        if idx in self._cache:
            sig = self._cache[idx]
        else:
            sig = load_record_lead_ii(path)
            if sig is None:
                sig = np.zeros(TARGET_SAMPLES, dtype=np.float32)

        x = torch.tensor(sig, dtype=torch.float32).unsqueeze(0)  # (1, 500)
        y = torch.tensor(label, dtype=torch.long)
        return x, y


def compute_class_weights(dataset: PTBXLDataset) -> "torch.Tensor":
    """Inverse-frequency class weights for imbalanced PTB-XL."""
    import torch
    counts = np.zeros(len(SUPERCLASS_LABELS), dtype=np.float32)
    for _, label in dataset.records:
        counts[label] += 1
    weights = counts.sum() / (len(counts) * counts + 1e-6)
    return torch.tensor(weights, dtype=torch.float32)


if __name__ == "__main__":
    import sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    ds = PTBXLDataset(data_dir, folds=[1], cache=False)
    x, y = ds[0]
    print(f"Signal shape: {x.shape}, Label: {SUPERCLASS_LABELS[y.item()]}")
    print(f"Dataset size: {len(ds)}")
