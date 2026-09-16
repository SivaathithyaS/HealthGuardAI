import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AnalysisContext(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: Optional[str] = None
    document_type_display: Optional[str] = None
    analysis_pathway: Optional[str] = None
    routing_confidence: float = 0.0
    patient_context: Dict[str, Any] = Field(default_factory=dict)
    extracted_features: List[Dict[str, Any]] = Field(default_factory=list)
    model_predictions: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_provenance: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    uncertainty_state: str = "HIGH_CONFIDENCE"
    warnings: List[str] = Field(default_factory=list)
    model_metadata: Dict[str, Any] = Field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)

    def log_event(self, stage: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        self.audit_trail.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "stage": stage,
            "message": message,
            "metadata": metadata or {}
        })

ANALYSIS_STORE: Dict[str, AnalysisContext] = {}

def create_fresh_analysis_context() -> AnalysisContext:
    ctx = AnalysisContext()
    ctx.log_event("INITIALIZATION", "Fresh isolated analysis context created. Previous state purged.")
    ANALYSIS_STORE[ctx.analysis_id] = ctx
    return ctx

def get_analysis_context(analysis_id: str) -> Optional[AnalysisContext]:
    return ANALYSIS_STORE.get(analysis_id)
