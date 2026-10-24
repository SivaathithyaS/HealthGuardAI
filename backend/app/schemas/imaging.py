from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class PredictionItem(BaseModel):
    label: str
    probability: float

class UncertaintyInfo(BaseModel):
    max_prob: float
    threshold: float
    ood_flag: bool = False

class SignalPreview(BaseModel):
    lead: str = "II"
    fs: int = 100
    samples: List[float] = Field(default_factory=list)

class ExplanationInfo(BaseModel):
    method: str = "grad-cam"
    heatmap_png_base64: Optional[str] = None
    saliency: Optional[List[float]] = None
    signal_preview: Optional[SignalPreview] = None

class TierMapping(BaseModel):
    level1_observed: str = ""
    level2_interpretation: str = ""
    level3_consideration: str = ""

class ImagingAnalysisResponse(BaseModel):
    request_id: str
    modality: str  # "ecg" | "mri"
    model_version: str
    status: str  # "ok" | "uncertain" | "rejected_input"
    reason: Optional[str] = None
    predictions: List[PredictionItem] = Field(default_factory=list)
    top_label: str = ""
    uncertainty: UncertaintyInfo
    explanation: Optional[ExplanationInfo] = None
    tier_mapping: TierMapping
    inference_ms: int = 0
    disclaimer: str = "Research prototype; not a diagnosis."

class ModelBundleSummary(BaseModel):
    name: str
    modality: str
    model_version: str
    stub: bool = False
    threshold: float = 0.6
    sha256_verified: bool = True
    labels: List[str] = Field(default_factory=list)
    description: str = ""
    weights_file: str = "weights.pt"

class SampleCase(BaseModel):
    id: str
    modality: str  # "ecg" | "mri"
    title: str
    description: str
    expected_status: str = "ok"  # "ok" | "uncertain" | "rejected_input"
    preview_tag: str = ""
