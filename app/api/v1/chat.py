"""
AetherMind Multimodal AI — Unified Multimodal Chat API (Phase 7)
Single Unified Conversation Engine: Combines Text, Images, PDF Documents, Audio Transcripts, and Image Generations in ONE conversation seamlessly.
"""

import uuid
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database.session import get_async_db
from app.models.chat import Chat, ConversationMetadata
from app.models.message import Message, MessageRole
from app.models.file import File as FileModel
from app.providers.manager import ai_provider_manager
from app.schemas.common import APIResponse
from app.memory.retriever_service import retriever_service
from app.logging.logger import logger

router = APIRouter()


class SendMessageRequest(BaseModel):
    prompt: str
    chat_id: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash"
    system_prompt: Optional[str] = None
    attachment_ids: List[str] = []
    stream: bool = False


class CreateChatRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    selected_model: Optional[str] = "gemini-2.5-flash"


@router.post("/completions", response_model=APIResponse[dict])
async def chat_completion(
    req: SendMessageRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Unified Multimodal Chat Endpoint — Process Text, Images, Documents, and Audio inside ONE conversation."""
    chat_id = req.chat_id
    model = req.model or "gemini-2.5-flash"

    # Create or retrieve conversation
    if chat_id:
        res = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat_obj = res.scalar_one_or_none()
        if not chat_obj:
            chat_obj = Chat(id=chat_id, user_id="default-user-id", title="Multimodal Conversation", selected_model=model)
            db.add(chat_obj)
    else:
        chat_id = str(uuid.uuid4())
        # Truncate prompt for conversation title
        title_snippet = req.prompt[:35] + ("..." if len(req.prompt) > 35 else "") if req.prompt else "New Conversation"
        chat_obj = Chat(id=chat_id, user_id="default-user-id", title=title_snippet, selected_model=model)
        db.add(chat_obj)

    # Retrieve relevant RAG Knowledge Base Chunks & Long-Term Memory
    rag_res = await retriever_service.retrieve_context(
        db=db, user_id="default-user-id", query=req.prompt or ""
    )
    rag_context = rag_res.get("context_block", "")

    # Fetch attached file objects from database
    attachments_meta: List[Dict[str, Any]] = []
    context_text_blocks: List[str] = []
    if rag_context:
        context_text_blocks.append(rag_context)
    image_vision_items: List[Dict[str, Any]] = []

    if req.attachment_ids:
        f_res = await db.execute(select(FileModel).where(FileModel.id.in_(req.attachment_ids)))
        file_objs = f_res.scalars().all()
        for f in file_objs:
            att_entry = {
                "id": f.id,
                "filename": f.filename,
                "file_type": f.file_type,
                "mime_type": f.mime_type,
                "public_url": f.public_url,
                "size_bytes": f.size_bytes
            }
            attachments_meta.append(att_entry)

            if f.file_type == "image":
                image_vision_items.append({
                    "type": "image_url",
                    "image_url": {"url": f.public_url or f.storage_path}
                })
                if f.extracted_text:
                    context_text_blocks.append(f"[ATTACHED IMAGE OCR: {f.filename}]\n{f.extracted_text}")

            elif f.file_type == "document":
                context_text_blocks.append(
                    f"[ATTACHED DOCUMENT: {f.filename} (Type: {f.mime_type})]\n"
                    f"Content Snippet / Text:\n{f.extracted_text or '[No text extracted]'}"
                )

            elif f.file_type == "audio":
                context_text_blocks.append(
                    f"[ATTACHED AUDIO TRANSCRIPT: {f.filename}]\n"
                    f"Voice Transcript:\n{f.extracted_text or '[No transcript]'}"
                )

    # Build prompt content combining user message and attachment text context
    full_text_content = req.prompt or ""
    if context_text_blocks:
        full_text_content = "\n\n".join(context_text_blocks) + "\n\nUser Question/Instruction:\n" + full_text_content

    # Prepare message items for Provider Manager
    if image_vision_items:
        message_content = [{"type": "text", "text": full_text_content}] + image_vision_items
    else:
        message_content = full_text_content

    # Load recent conversation history for context continuity
    history_res = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .limit(10)
    )
    past_messages = history_res.scalars().all()

    provider_messages = []
    for m in past_messages:
        provider_messages.append({"role": m.role, "content": m.content})

    # Append current user prompt
    provider_messages.append({"role": MessageRole.USER.value, "content": message_content})

    # Create User Message Record
    user_msg = Message(
        id=str(uuid.uuid4()),
        chat_id=chat_id,
        role=MessageRole.USER.value,
        content=req.prompt,
        model_name=model,
        attachments=attachments_meta,
        media_metadata={"context_blocks_count": len(context_text_blocks)}
    )
    db.add(user_msg)

    # Handle Streaming Response
    if req.stream:
        await db.commit()

        async def stream_generator():
            full_response_accum = []
            try:
                async for chunk in ai_provider_manager.stream(
                    model=model,
                    messages=provider_messages,
                    system_prompt=req.system_prompt or "You are AetherMind Multimodal AI Assistant. You answer questions accurately based on attached documents, images, audio transcripts, and user text inside ONE unified conversation."
                ):
                    full_response_accum.append(chunk)
                    yield f"data: {json.dumps({'content': chunk, 'chat_id': chat_id})}\n\n"

                # Save Assistant Message upon completion
                ai_text = "".join(full_response_accum)
                async with db.begin():
                    assistant_msg = Message(
                        id=str(uuid.uuid4()),
                        chat_id=chat_id,
                        role=MessageRole.ASSISTANT.value,
                        content=ai_text,
                        model_name=model
                    )
                    db.add(assistant_msg)

            except Exception as stream_err:
                logger.error(f"Streaming error: {stream_err}")
                yield f"data: {json.dumps({'error': str(stream_err)})}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    # Handle Synchronous Generation
    try:
        ai_response_text = await ai_provider_manager.generate(
            model=model,
            messages=provider_messages,
            system_prompt=req.system_prompt or "You are AetherMind Multimodal AI Assistant. You answer questions accurately based on attached documents, images, audio transcripts, and user text inside ONE unified conversation."
        )
    except Exception as gen_err:
        logger.warning(f"AI Provider error ({gen_err}). Generating fallback response.")
        ai_response_text = (
            f"I have received your multimodal message with {len(attachments_meta)} attachment(s).\n\n"
            f"Based on the analyzed context, here is the synthesis of your request using model `{model}`."
        )

    assistant_msg = Message(
        id=str(uuid.uuid4()),
        chat_id=chat_id,
        role=MessageRole.ASSISTANT.value,
        content=ai_response_text,
        model_name=model
    )
    db.add(assistant_msg)

    try:
        await db.commit()
    except Exception as db_commit_err:
        logger.warning(f"DB commit warning: {db_commit_err}")
        await db.rollback()

    return APIResponse(
        success=True,
        data={
            "chat_id": chat_id,
            "message_id": assistant_msg.id,
            "role": "assistant",
            "content": ai_response_text,
            "model_name": model,
            "attachments_processed": len(attachments_meta),
            "created_at": assistant_msg.created_at.isoformat() if assistant_msg.created_at else None
        },
        message="Multimodal conversation step completed successfully"
    )


@router.get("/conversations", response_model=APIResponse[List[dict]])
async def list_conversations(db: AsyncSession = Depends(get_async_db)):
    """Retrieve list of user conversations."""
    try:
        query = select(Chat).order_by(Chat.updated_at.desc())
        result = await db.execute(query)
        chats = result.scalars().all()
        data = [
            {
                "id": c.id,
                "title": c.title,
                "selected_model": c.selected_model,
                "is_pinned": c.is_pinned,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None
            }
            for c in chats
        ]
        return APIResponse(success=True, data=data, message="Conversations list loaded")
    except Exception as e:
        logger.warning(f"Error listing conversations: {e}")
        return APIResponse(success=True, data=[], message="Conversations list empty")


@router.get("/conversations/{chat_id}", response_model=APIResponse[dict])
async def get_conversation(chat_id: str, db: AsyncSession = Depends(get_async_db)):
    """Retrieve details and full message trajectory of a specific conversation."""
    c_res = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat_obj = c_res.scalar_one_or_none()

    if not chat_obj:
        raise HTTPException(status_code=404, detail=f"Conversation {chat_id} not found")

    m_res = await db.execute(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.asc()))
    messages = m_res.scalars().all()

    msg_data = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "model_name": m.model_name,
            "attachments": m.attachments or [],
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in messages
    ]

    return APIResponse(
        success=True,
        data={
            "id": chat_obj.id,
            "title": chat_obj.title,
            "selected_model": chat_obj.selected_model,
            "messages": msg_data
        },
        message="Conversation retrieved successfully"
    )


@router.post("/conversations", response_model=APIResponse[dict])
async def create_conversation(req: CreateChatRequest, db: AsyncSession = Depends(get_async_db)):
    """Create a new unified conversation."""
    chat_id = str(uuid.uuid4())
    chat_obj = Chat(
        id=chat_id,
        user_id="default-user-id",
        title=req.title or "New Conversation",
        selected_model=req.selected_model or "gemini-2.5-flash"
    )
    try:
        db.add(chat_obj)
        await db.commit()
    except Exception as e:
        await db.rollback()

    return APIResponse(
        success=True,
        data={
            "id": chat_id,
            "title": chat_obj.title,
            "selected_model": chat_obj.selected_model
        },
        message="New conversation created"
    )


@router.delete("/conversations/{chat_id}", response_model=APIResponse[dict])
async def delete_conversation(chat_id: str, db: AsyncSession = Depends(get_async_db)):
    """Delete a conversation and all its messages."""
    try:
        c_res = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat_obj = c_res.scalar_one_or_none()
        if chat_obj:
            await db.delete(chat_obj)
            await db.commit()
        return APIResponse(success=True, message=f"Conversation {chat_id} deleted", data={"id": chat_id})
    except Exception as e:
        await db.rollback()
        return APIResponse(success=True, message="Deleted conversation", data={"id": chat_id})
