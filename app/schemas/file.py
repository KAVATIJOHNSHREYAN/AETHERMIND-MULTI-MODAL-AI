from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str # 'document', 'image', 'audio', 'video'
    mime_type: str
    size_bytes: int
    public_url: Optional[str] = None
    extracted_text_snippet: Optional[str] = None
    media_metadata: Dict[str, Any] = {}
    created_at: datetime

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for AI Image Generation")
    negative_prompt: Optional[str] = None
    aspect_ratio: Optional[str] = "1:1" # '1:1', '16:9', '9:16'
    quality: Optional[str] = "standard"
    model: Optional[str] = "gemini-2.5-flash"

class ImageGenerationResponse(BaseModel):
    id: str
    prompt: str
    aspect_ratio: str
    image_url: str
    created_at: datetime

class VisionAnalysisRequest(BaseModel):
    image_url: str
    query: Optional[str] = "Describe this image in detail and extract all visible text via OCR."

class VisionAnalysisResponse(BaseModel):
    image_url: str
    analysis: str
    extracted_text: Optional[str] = None
    objects_detected: List[str] = []

class AudioTranscribeRequest(BaseModel):
    audio_url: str
    language: Optional[str] = "en"

class AudioTranscribeResponse(BaseModel):
    audio_url: str
    transcript: str
    duration_seconds: float = 0.0
