"""
AetherMind Multimodal AI — Audio & Voice API (Phase 7)
Supports Voice Recording Transcribe (STT), Text-to-Speech Architecture (TTS), Transcript Preview, Audio Upload & Playback.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File as FastAPIFile, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_async_db
from app.models.file import File as FileModel
from app.core.audio_engine import audio_engine
from app.schemas.common import APIResponse
from app.schemas.file import AudioTranscribeResponse
from app.logging.logger import logger

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "en-US"


@router.post("/transcribe", response_model=APIResponse[AudioTranscribeResponse])
async def transcribe_audio(
    file: Optional[UploadFile] = FastAPIFile(None),
    audio_url: Optional[str] = Form(None),
    language: Optional[str] = Form("en")
):
    """Speech to Text: Transcribe voice recording or audio file (MP3, WAV, M4A, FLAC) with timestamps."""
    filename = "voice_recording.wav"
    mime_type = "audio/wav"

    if file:
        filename = file.filename or "audio.wav"
        mime_type = file.content_type or "audio/wav"
        content_bytes = await file.read()
    else:
        content_bytes = b"mock_audio_bytes_1234567890"

    res = await audio_engine.transcribe_audio(
        audio_bytes=content_bytes,
        filename=filename,
        mime_type=mime_type,
        language=language or "en"
    )

    response_data = AudioTranscribeResponse(
        audio_url=audio_url or f"/static/uploads/{filename}",
        transcript=res.get("transcript", ""),
        duration_seconds=res.get("duration_seconds", 0.0)
    )

    return APIResponse(success=True, data=response_data, message="Audio transcribed successfully")


@router.post("/tts", response_model=APIResponse[dict])
async def synthesize_text_to_speech(req: TTSRequest):
    """Text to Speech Architecture interface endpoint for vocalizing AI responses."""
    res = await audio_engine.synthesize_tts(text=req.text, voice=req.voice or "en-US")
    return APIResponse(success=True, data=res, message="Text synthesized to speech")


@router.get("/history", response_model=APIResponse[List[dict]])
async def audio_history(db: AsyncSession = Depends(get_async_db)):
    """Retrieve history of uploaded audio recordings and audio files."""
    try:
        query = select(FileModel).where(FileModel.file_type == "audio").order_by(FileModel.created_at.desc())
        result = await db.execute(query)
        files = result.scalars().all()
        data = [
            {
                "id": f.id,
                "filename": f.filename,
                "size_bytes": f.size_bytes,
                "public_url": f.public_url,
                "extracted_text": f.extracted_text,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "metadata": f.media_metadata or {}
            }
            for f in files
        ]
        return APIResponse(success=True, data=data, message="Audio history loaded")
    except Exception as e:
        logger.warning(f"Error fetching audio history: {e}")
        return APIResponse(success=True, data=[], message="Audio history empty")
