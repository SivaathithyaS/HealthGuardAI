"""
Trains the heart disease hybrid ensemble and saves it (plus feature order and
a SHAP explainer) as a single pickle artifact the backend loads at startup.

Run once: python train_heart_model.py
"""
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
import shap

HERE = __file__.rsplit("/", 1)[0]

df = pd.read_csv(f"{HERE}/heart.csv")
FEATURE_ORDER = [c for c in df.columns if c != "target"]
X = df[FEATURE_ORDER]
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

rf = RandomForestClassifier(n_estimators=200, random_state=42).fit(X_train, y_train)
xgb = XGBClassifier(eval_metric="logloss", random_state=42).fit(X_train, y_train)
dt = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)

ensemble = VotingClassifier(
    estimators=[("rf", rf), ("xgb", xgb), ("dt", dt)], voting="soft"
)
ensemble.fit(X_train, y_train)

# SHAP explanations come from the XGBoost member (fast, well-supported TreeExplainer).
# The ensemble drives the risk score shown to the user; XGBoost's SHAP values drive
# the "why" — a reasonable approximation since XGBoost is one of the three voters.
explainer = shap.TreeExplainer(xgb)

artifact = {
    "ensemble_model": ensemble,
    "explainer_model": xgb,
    "shap_explainer": explainer,
    "feature_order": FEATURE_ORDER,
    "feature_medians": X_train.median().to_dict(),  # used for what-if baselines
}

with open(f"{HERE}/heart_pipeline.pkl", "wb") as f:
    pickle.dump(artifact, f)

print(f"Saved heart_pipeline.pkl with {len(FEATURE_ORDER)} features: {FEATURE_ORDER}")
print(f"Train accuracy: {ensemble.score(X_train, y_train):.3f}")
print(f"Test accuracy: {ensemble.score(X_test, y_test):.3f}")
