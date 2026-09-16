import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import shap

# URL for UCI Cleveland Heart Disease dataset
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", 
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
]

def load_data():
    print("Fetching UCI Cleveland Heart Disease dataset...")
    df = pd.read_csv(DATA_URL, names=COLUMNS, na_values="?")
    
    # Impute missing values with medians
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
            
    # Binary classification: 0 = no disease, 1 = disease present
    df["target"] = (df["target"] > 0).astype(int)
    
    X = df.drop(columns=["target"])
    y = df["target"]
    
    return X, y

def train_and_evaluate():
    X, y = load_data()
    print(f"Total patient samples: {len(X)}, Features: {X.shape[1]}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 1. Random Forest Classifier
    rf = RandomForestClassifier(
        n_estimators=150, max_depth=5, min_samples_split=4, random_state=42
    )
    
    # 2. Gradient Boosting Classifier
    gb = GradientBoostingClassifier(
        n_estimators=120, max_depth=3, learning_rate=0.05, random_state=42
    )
    
    # 3. Soft Voting Ensemble
    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("gb", gb)],
        voting="soft"
    )
    
    print("Fitting models...")
    rf.fit(X_train, y_train)
    gb.fit(X_train, y_train)
    ensemble.fit(X_train, y_train)
    
    y_pred = ensemble.predict(X_test)
    y_proba = ensemble.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    print(f"Ensemble Evaluation Metrics on Test Set:")
    print(f" - Accuracy:  {acc:.4f}")
    print(f" - Precision: {prec:.4f}")
    print(f" - Recall:    {rec:.4f}")
    print(f" - F1 Score:  {f1:.4f}")
    print(f" - ROC AUC:   {auc:.4f}")
    
    # Initialize TreeSHAP explainer on the Gradient Boosting model
    explainer = shap.TreeExplainer(gb)
    
    # Calculate feature summary stats for validation and slider bounds
    feature_stats = {}
    for col in X.columns:
        feature_stats[col] = {
            "min": float(X[col].min()),
            "max": float(X[col].max()),
            "mean": round(float(X[col].mean()), 2),
            "median": float(X[col].median())
        }
        
    pipeline_artifact = {
        "ensemble_model": ensemble,
        "gb_model": gb,
        "rf_model": rf,
        "shap_explainer": explainer,
        "feature_names": list(X.columns),
        "feature_stats": feature_stats,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(auc, 4)
        }
    }
    
    os.makedirs("backend/data", exist_ok=True)
    out_file = "backend/data/heart_pipeline.pkl"
    joblib.dump(pipeline_artifact, out_file)
    print(f"Successfully serialized pipeline to {out_file}")

if __name__ == "__main__":
    train_and_evaluate()
