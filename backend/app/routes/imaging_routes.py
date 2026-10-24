from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List

from backend.app.schemas.imaging import (
    ImagingAnalysisResponse,
    ModelBundleSummary,
    SampleCase
)
from backend.app.services.cnn_service import cnn_service

router = APIRouter(prefix="/api/imaging", tags=["Clinical Imaging & Waveforms"])

@router.post("/ecg", response_model=ImagingAnalysisResponse)
async def analyze_ecg_endpoint(file: UploadFile = File(...)):
    """Uploads a raw ECG voltage file or strip image for 1D-CNN temporal rhythm classification."""
    try:
        raw_bytes = await file.read()
        return cnn_service.analyze_ecg(raw_bytes=raw_bytes, filename=file.filename or "uploaded_ecg.dat")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed processing ECG upload: {str(e)}")

@router.post("/mri", response_model=ImagingAnalysisResponse)
async def analyze_mri_endpoint(file: UploadFile = File(...)):
    """Uploads an axial brain MRI slice (DICOM/PNG/JPG) for 2D DenseNet classification & Grad-CAM."""
    try:
        raw_bytes = await file.read()
        return cnn_service.analyze_mri(raw_bytes=raw_bytes, filename=file.filename or "uploaded_mri.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed processing MRI upload: {str(e)}")

@router.get("/models", response_model=Dict[str, List[ModelBundleSummary]])
def get_imaging_models():
    """Lists loaded imaging model bundles, SHA-256 validation status, and operational thresholds."""
    return {"models": cnn_service.list_models()}

@router.get("/samples", response_model=Dict[str, List[SampleCase]])
def get_imaging_samples():
    """Returns curated diagnostic ECG rhythm strips and brain MRI slices for live clinical testing."""
    return {"samples": cnn_service.list_samples()}

@router.post("/{modality}/sample/{sample_id}", response_model=ImagingAnalysisResponse)
def analyze_sample_case(modality: str, sample_id: str):
    """Executes inference on a predefined clinical sample case without requiring local file upload."""
    return cnn_service.analyze_sample(modality=modality, sample_id=sample_id)
