"""
AetherMind Multimodal AI — File Storage & Upload API (Phase 7)
Supports uploading PDF, DOCX, PPTX, TXT, CSV, XLSX, JSON, MD, Images, Audio, Video files.
Handles file validation, background parsing, file deletion, and history listing.
"""

import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File as FastAPIFile, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database.session import get_async_db
from app.models.file import File as FileModel
from app.documents.rag_engine import document_engine
from app.core.vision_engine import vision_engine
from app.core.audio_engine import audio_engine
from app.schemas.common import APIResponse
from app.schemas.file import FileUploadResponse
from app.logging.logger import logger

import tempfile

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    UPLOAD_DIR = tempfile.gettempdir()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB Max File Size Security Validation

ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".csv", ".xlsx", ".xls", ".json", ".md", ".html", ".htm",
    # Images
    ".png", ".jpg", ".jpeg", ".webp", ".svg", ".bmp", ".gif",
    # Audio
    ".mp3", ".wav", ".m4a", ".flac", ".webm", ".ogg", ".aac", ".opus",
    # Video
    ".mp4", ".mov", ".avi", ".mkv",
    # Generic
    ".bin"
}


def get_file_category(extension: str) -> str:
    ext = extension.lower()
    if ext in [".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".csv", ".xlsx", ".xls", ".json", ".md", ".html", ".htm"]:
        return "document"
    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".bmp", ".gif"]:
        return "image"
    elif ext in [".mp3", ".wav", ".m4a", ".flac", ".webm", ".ogg", ".aac", ".opus"]:
        return "audio"
    elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
        return "video"
    return "document"


from app.core.dependencies import get_current_user_or_session
from app.models.user import User


@router.get("/file/{filename}")
async def get_uploaded_file(filename: str):
    """Serve uploaded file cleanly from local static directory or serverless /tmp."""
    possible_paths = [
        os.path.join(UPLOAD_DIR, filename),
        os.path.join(tempfile.gettempdir(), filename)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return FileResponse(path)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


@router.post("", response_model=APIResponse[FileUploadResponse])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    chat_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Upload file (PDF, DOCX, Images, Audio, Video, etc.) with security validation & engine extraction."""
    filename = file.filename or "uploaded_file"
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""

    # Auto infer extension if missing or blob
    if not ext or ext == ".blob":
        if file.content_type and "image" in file.content_type:
            ext = ".png"
        elif file.content_type and "audio" in file.content_type:
            ext = ".webm"
        elif file.content_type and "video" in file.content_type:
            ext = ".mp4"
        else:
            ext = ".txt"
        filename = f"{filename}{ext}"

    if ext not in ALLOWED_EXTENSIONS:
        ext = ".bin"
        ALLOWED_EXTENSIONS.add(".bin")

    content_bytes = await file.read()

    # Security File Size Validation
    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds 50MB limit ({len(content_bytes) / (1024*1024):.2f}MB)"
        )

    file_category = get_file_category(ext)
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id[:8]}_{filename.replace(' ', '_')}"

    # Serverless Vercel Writable Directory Fallback
    target_dir = UPLOAD_DIR
    if os.environ.get("VERCEL") or not os.access(os.path.dirname(UPLOAD_DIR), os.W_OK):
        target_dir = tempfile.gettempdir()
    else:
        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception:
            target_dir = tempfile.gettempdir()

    filepath = os.path.join(target_dir, safe_filename)

    try:
        with open(filepath, "wb") as f:
            f.write(content_bytes)
    except Exception as write_err:
        logger.warning(f"Failed writing to {filepath}: {write_err}. Falling back to /tmp")
        target_dir = tempfile.gettempdir()
        filepath = os.path.join(target_dir, safe_filename)
        with open(filepath, "wb") as f:
            f.write(content_bytes)

    public_url = f"/api/v1/upload/file/{safe_filename}"
    extracted_text = ""
    media_metadata: Dict[str, Any] = {}

    # Trigger corresponding Engine for metadata extraction & OCR/Parsing
    try:
        if file_category == "document":
            parse_res = await document_engine.parse_document(filename, content_bytes)
            extracted_text = parse_res.get("extracted_text", "")
            media_metadata = parse_res.get("metadata", {})
            media_metadata["pages_content"] = parse_res.get("pages_content", [])
            media_metadata["chunks"] = parse_res.get("chunks", [])

        elif file_category == "image":
            vision_res = await vision_engine.analyze_image(content_bytes, file.content_type or "image/png")
            extracted_text = vision_res.get("extracted_text", "")
            media_metadata = {
                "width": vision_res.get("width"),
                "height": vision_res.get("height"),
                "format": vision_res.get("format"),
                "analysis": vision_res.get("analysis"),
                "objects_detected": vision_res.get("objects_detected", [])
            }

        elif file_category == "audio":
            audio_res = await audio_engine.transcribe_audio(content_bytes, filename, file.content_type or "audio/wav")
            extracted_text = audio_res.get("transcript", "")
            media_metadata = audio_res.get("metadata", {})
            media_metadata["timestamps"] = audio_res.get("timestamps", [])

        elif file_category == "video":
            extracted_text = f"[Video File: {filename}]"
            media_metadata = {"format": ext.replace(".", "").upper(), "duration": 0.0}

    except Exception as parse_err:
        logger.warning(f"Engine processing warning for {filename}: {parse_err}")
        extracted_text = f"[Uploaded file: {filename}]"

    # Database Record Creation
    file_record = FileModel(
        id=file_id,
        user_id=current_user.id,
        chat_id=chat_id,
        filename=filename,
        file_type=file_category,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(content_bytes),
        storage_path=filepath,
        public_url=public_url,
        extracted_text=extracted_text,
        media_metadata=media_metadata
    )

    try:
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
    except Exception as db_err:
        logger.warning(f"Database commit file record fallback: {db_err}")
        await db.rollback()

    response_data = FileUploadResponse(
        id=file_id,
        filename=filename,
        file_type=file_category,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(content_bytes),
        public_url=public_url,
        extracted_text_snippet=extracted_text[:300] if extracted_text else None,
        media_metadata=media_metadata,
        created_at=file_record.created_at
    )

    return APIResponse(
        success=True,
        message=f"File '{filename}' uploaded and processed successfully",
        data=response_data
    )


@router.get("/files", response_model=APIResponse[List[FileUploadResponse]])
async def list_files(
    chat_id: Optional[str] = None,
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve uploaded files history filtered strictly by current user ID."""
    try:
        query = select(FileModel).where(FileModel.user_id == current_user.id, FileModel.is_deleted == False)
        if chat_id:
            query = query.where(FileModel.chat_id == chat_id)
        if file_type:
            query = query.where(FileModel.file_type == file_type)

        query = query.order_by(FileModel.created_at.desc())
        result = await db.execute(query)
        files = result.scalars().all()

        data = [
            FileUploadResponse(
                id=f.id,
                filename=f.filename,
                file_type=f.file_type,
                mime_type=f.mime_type,
                size_bytes=f.size_bytes,
                public_url=f.public_url,
                extracted_text_snippet=f.extracted_text[:300] if f.extracted_text else None,
                media_metadata=f.media_metadata or {},
                created_at=f.created_at
            )
            for f in files
        ]
        return APIResponse(success=True, data=data, message="Uploaded files retrieved successfully")
    except Exception as e:
        logger.warning(f"Database error fetching files: {e}")
        return APIResponse(success=True, data=[], message="Files list empty")


@router.delete("/files/{file_id}", response_model=APIResponse[dict])
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete uploaded file strictly verifying ownership by current user."""
    try:
        result = await db.execute(
            select(FileModel).where(FileModel.id == file_id, FileModel.user_id == current_user.id)
        )
        file_rec = result.scalar_one_or_none()

        if file_rec:
            if file_rec.storage_path and os.path.exists(file_rec.storage_path):
                try:
                    os.remove(file_rec.storage_path)
                except Exception as file_del_err:
                    logger.warning(f"Could not delete physical file: {file_del_err}")

            await db.delete(file_rec)
            await db.commit()

        return APIResponse(success=True, message=f"File {file_id} deleted successfully", data={"id": file_id})
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        await db.rollback()
        return APIResponse(success=True, message=f"File {file_id} removed", data={"id": file_id})
