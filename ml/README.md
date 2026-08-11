# ML/Data

- `data/raw/`        Original downloaded datasets (heart, diabetes, ckd) — gitignored, not committed
- `data/processed/`  Cleaned/feature-engineered versions — gitignored, not committed
- `notebooks/`       EDA and experimentation notebooks
- `src/`             Reusable training/preprocessing/SHAP code (not notebook-only)
- `models/`          Saved trained model artifacts (.pkl/.joblib) — gitignored, not committed

Datasets should be documented (source, license, download date) in this README
once chosen, not committed directly to the repo — keep the repo light and
avoid redistributing datasets that may have license restrictions.
