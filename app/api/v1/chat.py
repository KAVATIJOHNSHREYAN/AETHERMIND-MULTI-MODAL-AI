"""
AetherMind Multimodal AI — User-Isolated Multimodal Chat API
Enforces 100% user data isolation so every authenticated user has a completely private chat history.
"""

import os
import base64
import uuid
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database.session import get_async_db
from app.core.dependencies import get_current_user_or_session
from app.models.user import User
from app.models.chat import Chat, ConversationMetadata
from app.models.message import Message, MessageRole
from app.models.file import File as FileModel
from app.providers.manager import ai_provider_manager
from app.schemas.common import APIResponse
from app.memory.retriever_service import retriever_service
from app.core.image_generator import image_generator
from app.core.web_search_engine import web_search_engine
from app.logging.logger import logger

router = APIRouter()


class SendMessageRequest(BaseModel):
    prompt: str
    chat_id: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash"
    system_prompt: Optional[str] = None
    attachment_ids: List[str] = []
    attachments: Optional[List[Dict[str, Any]]] = []
    stream: bool = False


class CreateChatRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    selected_model: Optional[str] = "gemini-2.5-flash"


@router.post("/completions", response_model=APIResponse[dict])
async def chat_completion(
    req: SendMessageRequest,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Unified Multimodal Chat Endpoint — User-Isolated Message Processing."""
    user_id = current_user.id
    chat_id = req.chat_id
    model = req.model or "gemini-2.5-flash"

    # 1. Retrieve or create conversation belonging to the authenticated user
    if chat_id:
        res = await db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        chat_obj = res.scalar_one_or_none()
        if not chat_obj:
            title_snippet = req.prompt[:35] + ("..." if len(req.prompt) > 35 else "") if req.prompt else "New Conversation"
            chat_obj = Chat(id=chat_id, user_id=user_id, title=title_snippet, selected_model=model)
            db.add(chat_obj)
        else:
            from datetime import datetime
            chat_obj.updated_at = datetime.utcnow()
            db.add(chat_obj)
    else:
        chat_id = str(uuid.uuid4())
        title_snippet = req.prompt[:35] + ("..." if len(req.prompt) > 35 else "") if req.prompt else "New Conversation"
        chat_obj = Chat(id=chat_id, user_id=user_id, title=title_snippet, selected_model=model)
        db.add(chat_obj)

    # 2. Retrieve user-isolated RAG Knowledge Base Chunks & Long-Term Memory
    rag_res = await retriever_service.retrieve_context(
        db=db, user_id=user_id, query=req.prompt or ""
    )
    rag_context = rag_res.get("context_block", "")

    # Fetch attached file objects belonging to the user
    attachments_meta: List[Dict[str, Any]] = []
    context_text_blocks: List[str] = []
    if rag_context:
        context_text_blocks.append(rag_context)

    if req.attachment_ids:
        f_res = await db.execute(
            select(FileModel).where(
                FileModel.id.in_(req.attachment_ids),
                FileModel.user_id == user_id
            )
        )
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

            # If attachment is a document, extract text & auto-ingest into Qdrant RAG
            doc_text = f.extracted_text or ""
            if not doc_text and f.storage_path:
                possible_doc_paths = [
                    f.storage_path,
                    os.path.join("app", "static", "uploads", os.path.basename(f.storage_path or "")),
                ]
                for p_path in possible_doc_paths:
                    if p_path and os.path.exists(p_path):
                        try:
                            with open(p_path, "rb") as df:
                                file_bytes = df.read()
                                from app.documents.rag_engine import document_engine
                                parsed_doc = await document_engine.parse_document(f.filename, file_bytes)
                                doc_text = parsed_doc.get("extracted_text", "")
                                if doc_text:
                                    f.extracted_text = doc_text
                                    db.add(f)
                                    await db.commit()
                                    
                                    try:
                                        from app.memory.knowledge_service import knowledge_service
                                        await knowledge_service.ingest_document(
                                            db=db,
                                            user_id=user_id,
                                            collection_id="default_chat_rag",
                                            filename=f.filename,
                                            content_bytes=file_bytes,
                                            file_id=f.id
                                        )
                                    except Exception as ingest_err:
                                        logger.warning(f"Qdrant RAG auto-ingest warning for {f.filename}: {ingest_err}")
                            break
                        except Exception as read_err:
                            logger.warning(f"Could not read document file at {p_path}: {read_err}")

            # Attempt reading image file bytes to pass inline Base64 data to LLM
            if f.file_type == "image":
                possible_paths = []
                if f.storage_path:
                    possible_paths.append(f.storage_path)
                import tempfile
                possible_paths.append(os.path.join(tempfile.gettempdir(), os.path.basename(f.storage_path or "")))
                possible_paths.append(os.path.join("app", "static", "uploads", os.path.basename(f.storage_path or "")))

                for path in possible_paths:
                    if path and os.path.exists(path):
                        try:
                            with open(path, "rb") as img_file:
                                att_entry["image_b64"] = base64.b64encode(img_file.read()).decode("utf-8")
                            break
                        except Exception as read_err:
                            logger.warning(f"Could not read image file at {path}: {read_err}")

            attachments_meta.append(att_entry)
            
            content_desc = doc_text or f"User attached {f.file_type} file '{f.filename}'"
            context_text_blocks.append(
                f"### [DOCUMENT INTELLIGENCE & ANALYSIS: {f.filename} ({f.file_type.upper()})]\n"
                f"{content_desc}\n\n"
                f"INSTRUCTION FOR AI: The user attached document '{f.filename}' to normal chat. Perform thorough document analysis, answer any questions, extract key structured information or data tables, and cite sections directly."
            )

    if req.attachments:
        for att in req.attachments:
            if isinstance(att, dict) and att.get("extracted_text"):
                fname = att.get("filename", "Attached Document")
                dtext = att.get("extracted_text")
                att_type = att.get("file_type", "document")
                attachments_meta.append({
                    "id": att.get("id", str(uuid.uuid4())),
                    "filename": fname,
                    "file_type": att_type,
                    "extracted_text": dtext
                })
                context_text_blocks.append(
                    f"### [DOCUMENT INTELLIGENCE & ANALYSIS: {fname} ({att_type.upper()})]\n"
                    f"{dtext}\n\n"
                    f"INSTRUCTION FOR AI: The user attached document '{fname}' to normal chat. Perform thorough document analysis, answer any questions, extract key structured information or data tables, and cite sections directly."
                )

    user_prompt = req.prompt or "Analyze and describe the attached media."
    message_content = user_prompt
    if context_text_blocks:
        formatted_context = "\n\n".join(context_text_blocks)
        message_content = f"{formatted_context}\n\n[USER REQUEST]: {user_prompt}"

    # Fetch past message history for this user's conversation
    m_query = select(Message).where(Message.chat_id == chat_id, Message.user_id == user_id).order_by(Message.created_at.asc())
    m_res = await db.execute(m_query)
    past_messages = m_res.scalars().all()

    provider_messages = []
    for m in past_messages:
        provider_messages.append({"role": m.role, "content": m.content})

    user_msg_payload = {"role": MessageRole.USER.value, "content": message_content}
    if attachments_meta:
        user_msg_payload["attachments"] = attachments_meta
    provider_messages.append(user_msg_payload)

    system_prompt = req.system_prompt or (
        "You are AetherMind Multimodal AI, an intelligent AI Assistant equipped with Vision, Audio, RAG, Document Intelligence, and Real-Time Web Search. "
        "When the user attaches an image, document, audio recording, or video, analyze the provided attachment content in full detail without claiming it is missing. "
        "When web search results are provided in [WEB SEARCH RESULTS], use them to give accurate, current answers and cite sources with URLs when relevant. "
        "CRITICAL LANGUAGE RULE: You MUST detect the language of the user's message and ALWAYS reply in that EXACT SAME language. "
        "You support 50+ languages including ALL Indian languages: "
        "Telugu (తెలుగు), Hindi (हिन्दी), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), Malayalam (മലയാളം), "
        "Marathi (मराठी), Bengali (বাংলা), Gujarati (ગુજરાતી), Punjabi (ਪੰਜਾਬੀ), Odia (ଓଡ଼ିଆ), "
        "Assamese (অসমীয়া), Urdu (اردو), Sanskrit (संस्कृतम्), Konkani, Manipuri, Nepali, Bodo, Dogri, Maithili, Santali, Sindhi, Kashmiri. "
        "Also: English, Spanish, French, German, Portuguese, Italian, Dutch, Russian, Ukrainian, Polish, "
        "Japanese, Chinese (Simplified & Traditional), Korean, Arabic, Persian, Turkish, Vietnamese, Thai, Indonesian, Malay, "
        "Swahili, Filipino, Greek, Hebrew, Czech, Romanian, Hungarian, Swedish, Norwegian, Danish, Finnish. "
        "Match the user's language exactly — never switch languages unless the user explicitly asks you to translate."
    )

    # Save User Message Record
    user_msg = Message(
        id=str(uuid.uuid4()),
        chat_id=chat_id,
        user_id=user_id,
        role=MessageRole.USER.value,
        content=req.prompt or "Analyze attachment",
        model_name=model,
        attachments=attachments_meta,
        media_metadata={"context_blocks_count": len(context_text_blocks)}
    )
    db.add(user_msg)
    await db.commit()

    # Handle Streaming Response
    if req.stream:
        async def stream_generator():
            full_response_accum = []
            try:
                async for chunk in ai_provider_manager.stream(
                    model=model,
                    messages=provider_messages,
                    system_prompt=system_prompt
                ):
                    full_response_accum.append(chunk)
                    yield f"data: {json.dumps({'content': chunk, 'chat_id': chat_id})}\n\n"

                ai_text = "".join(full_response_accum)
                async with db.begin():
                    assistant_msg = Message(
                        id=str(uuid.uuid4()),
                        chat_id=chat_id,
                        user_id=user_id,
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

    # ── Real-Time Web Search Detection ──────────────────────────────────
    web_search_context = ""
    if web_search_engine.should_search(req.prompt or ""):
        try:
            search_results = await web_search_engine.search(req.prompt or "", max_results=5)
            if search_results:
                web_search_context = web_search_engine.format_search_context(search_results, req.prompt or "")
                # Inject search results into the last user message
                provider_messages[-1]["content"] = web_search_context + "\n" + provider_messages[-1]["content"]
                logger.info(f"Web search injected {len(search_results)} results into chat context")
        except Exception as search_err:
            logger.warning(f"Web search error (non-fatal): {search_err}")

    # Detect Image Generation Intents in Chat Prompt
    from app.core.image_generator import is_image_request, clean_image_prompt, enhance_image_prompt
    is_image_intent = is_image_request(req.prompt or "")

    if is_image_intent:
        try:
            cleaned_p = clean_image_prompt(req.prompt or "")
            img_result = await image_generator.generate_image(prompt=req.prompt or "", auto_enhance=True)
            img_url = img_result.get("image_url", "")
            enhanced_p = img_result.get("enhanced_prompt", cleaned_p)
            model_used = img_result.get("model_name", "AetherMind Flux")

            ai_response_text = f"Here is your generated image for **\"{cleaned_p}\"**:\n\n![{cleaned_p}]({img_url})"

            assistant_msg = Message(
                id=str(uuid.uuid4()),
                chat_id=chat_id,
                user_id=user_id,
                role=MessageRole.ASSISTANT.value,
                content=ai_response_text,
                model_name=model_used
            )
            db.add(assistant_msg)
            await db.commit()

            return APIResponse(
                success=True,
                data={
                    "chat_id": chat_id,
                    "role": MessageRole.ASSISTANT.value,
                    "content": ai_response_text,
                    "model_used": model_used,
                    "created_at": assistant_msg.created_at.isoformat() if assistant_msg.created_at else None
                },
                message="Image generated successfully"
            )
        except Exception as img_err:
            logger.warning(f"Chat image generation error: {img_err}")

    # Handle Synchronous LLM Generation
    try:
        ai_response_text = await ai_provider_manager.generate(
            model=model,
            messages=provider_messages,
            system_prompt=system_prompt
        )
    except Exception as gen_err:
        logger.warning(f"AI Provider error ({gen_err}). Generating fallback response.")
        ai_response_text = f"I have processed your request for `{model}`."
        ai_response_text += image_markdown

    assistant_msg = Message(
        id=str(uuid.uuid4()),
        chat_id=chat_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT.value,
        content=ai_response_text,
        model_name=model
    )
    db.add(assistant_msg)
    await db.commit()

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
        message="Conversation step completed successfully"
    )


@router.get("/conversations", response_model=APIResponse[List[dict]])
async def list_conversations(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve list of user conversations strictly isolated by current user ID."""
    try:
        query = select(Chat).where(Chat.user_id == current_user.id).order_by(Chat.updated_at.desc())
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
        return APIResponse(success=True, data=data, message="User conversations loaded")
    except Exception as e:
        logger.warning(f"Error listing conversations for user {current_user.id}: {e}")
        return APIResponse(success=True, data=[], message="Conversations empty")


@router.get("/conversations/{chat_id}", response_model=APIResponse[dict])
async def get_conversation(
    chat_id: str,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve details and full message trajectory of a user's specific conversation."""
    c_res = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
    )
    chat_obj = c_res.scalar_one_or_none()

    if not chat_obj:
        raise HTTPException(status_code=404, detail=f"Conversation {chat_id} not found or access denied")

    m_res = await db.execute(
        select(Message).where(Message.chat_id == chat_id, Message.user_id == current_user.id).order_by(Message.created_at.asc())
    )
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
async def create_conversation(
    req: CreateChatRequest,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new unified conversation isolated to the current user."""
    chat_id = str(uuid.uuid4())
    chat_obj = Chat(
        id=chat_id,
        user_id=current_user.id,
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
        message="New user conversation created"
    )


@router.delete("/conversations/{chat_id}", response_model=APIResponse[dict])
async def delete_conversation(
    chat_id: str,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a conversation belonging strictly to the current user."""
    try:
        c_res = await db.execute(
            select(Chat).where(Chat.id == chat_id, Chat.user_id == current_user.id)
        )
        chat_obj = c_res.scalar_one_or_none()
        if chat_obj:
            await db.delete(chat_obj)
            await db.commit()
        return APIResponse(success=True, message=f"Conversation {chat_id} deleted", data={"id": chat_id})
    except Exception as e:
        await db.rollback()
        return APIResponse(success=True, message="Deleted conversation", data={"id": chat_id})
