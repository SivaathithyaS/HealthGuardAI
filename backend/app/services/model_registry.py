from typing import Dict, Any, List
from pydantic import BaseModel

class ModelMetadata(BaseModel):
    model_id: str
    name: str
    version: str
    clinical_domain: str
    architecture: str
    training_dataset: str
    validation_status: str
    feature_schema_version: str
    validation_accuracy: float
    validation_roc_auc: float
    calibration_method: str
    status: str

MODEL_REGISTRY: Dict[str, ModelMetadata] = {
    "neurovascular_stroke": ModelMetadata(
        model_id="neurovascular_stroke_v1",
        name="Neurovascular Stroke & LVO Classifier",
        version="1.2.0",
        clinical_domain="Emergency Neuroradiology & Acute Stroke",
        architecture="Hierarchical Vessel Occlusion & Ischemic Hypoattenuation Classifier",
        training_dataset="Multicenter Acute Neurovascular CTA & Ischemic Stroke Cohort",
        validation_status="Retrospective clinical evaluation dataset (Not an independent prospective trial)",
        feature_schema_version="stroke_cta_schema_v1.2",
        validation_accuracy=0.968,
        validation_roc_auc=0.985,
        calibration_method="Isotonic Probability Calibration",
        status="ACTIVE"
    ),
    "neuro_oncology": ModelMetadata(
        model_id="neuro_oncology_v1",
        name="Neuro-Oncology Radiomics Classifier",
        version="1.4.0",
        clinical_domain="Neuroradiology & Neuro-Oncology",
        architecture="Hierarchical Morphologic & Spatial Radiomic Engine",
        training_dataset="Multicenter Glioma / High-Grade Intracranial Mass Benchmark",
        validation_status="Retrospective clinical evaluation dataset (Not an independent prospective trial)",
        feature_schema_version="nrad_schema_v1.4",
        validation_accuracy=0.942,
        validation_roc_auc=0.965,
        calibration_method="Isotonic Scaling",
        status="ACTIVE"
    ),
    "cardiovascular": ModelMetadata(
        model_id="cardio_ensemble_v1",
        name="Cardiovascular Risk Soft-Voting Ensemble",
        version="1.1.0",
        clinical_domain="Cardiology & Hemodynamics",
        architecture="Random Forest + Gradient Boosting + TreeSHAP",
        training_dataset="UCI Cleveland Heart Disease Cohort (N=303)",
        validation_status="Internal cross-validation on standard clinical benchmark",
        feature_schema_version="cardio_schema_v1.1",
        validation_accuracy=0.9016,
        validation_roc_auc=0.9524,
        calibration_method="Platt Sigmoidal Calibration",
        status="ACTIVE"
    ),
    "diabetes": ModelMetadata(
        model_id="diabetes_ensemble_v1",
        name="Type 2 Diabetes Risk Ensemble",
        version="1.1.0",
        clinical_domain="Endocrinology & Metabolism",
        architecture="Gradient Boosted Decision Trees + TreeSHAP",
        training_dataset="NIDDK Pima Indians Diabetes Dataset (N=768)",
        validation_status="Internal cross-validation on standard clinical benchmark",
        feature_schema_version="diab_schema_v1.1",
        validation_accuracy=0.7403,
        validation_roc_auc=0.8211,
        calibration_method="Isotonic Regression",
        status="ACTIVE"
    ),
    "ckd": ModelMetadata(
        model_id="ckd_ensemble_v1",
        name="Chronic Kidney Disease Screening Ensemble",
        version="1.1.0",
        clinical_domain="Nephrology & Renal Function",
        architecture="Random Forest Classifier + TreeSHAP",
        training_dataset="UCI Chronic Kidney Disease Benchmark (N=400)",
        validation_status="Internal cross-validation on standard clinical benchmark",
        feature_schema_version="ckd_schema_v1.1",
        validation_accuracy=0.9125,
        validation_roc_auc=0.9825,
        calibration_method="Platt Calibration",
        status="ACTIVE"
    ),
    "liver": ModelMetadata(
        model_id="liver_ensemble_v1",
        name="Hepatic & Liver Disease Classifier",
        version="1.1.0",
        clinical_domain="Hepatology & Hepatic Enzymes",
        architecture="Random Forest + Gradient Boosting",
        training_dataset="Indian Liver Patient Dataset (ILPD, N=583)",
        validation_status="Internal cross-validation on standard clinical benchmark",
        feature_schema_version="liver_schema_v1.1",
        validation_accuracy=0.6923,
        validation_roc_auc=0.7661,
        calibration_method="Isotonic Regression",
        status="ACTIVE"
    )
}

def get_model_registry() -> List[Dict[str, Any]]:
    return [m.model_dump() for m in MODEL_REGISTRY.values()]
