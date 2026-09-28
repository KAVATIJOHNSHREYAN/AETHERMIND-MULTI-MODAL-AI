"""
AetherMind Multimodal AI — Hybrid Search & Vector RAG API (Phase 8)
Supports Semantic Search, Keyword BM25 Search, Combined Hybrid Search, Reranking, and Search History.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_async_db
from app.memory.search_service import search_service
from app.models.memory import SearchHistory
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


class SearchQueryRequest(BaseModel):
    query: str
    search_type: Optional[str] = "hybrid" # hybrid, semantic, keyword
    collection_id: Optional[str] = None
    limit: Optional[int] = 10


from app.core.dependencies import get_current_user_or_session
from app.models.user import User

@router.post("", response_model=APIResponse[dict])
async def search_knowledge_and_memory(
    req: SearchQueryRequest,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Perform Semantic, Keyword, or Hybrid Vector RAG Search across Knowledge Base Collections and Long-Term Memory."""
    res = await search_service.execute_search(
        db=db,
        user_id=current_user.id,
        query=req.query,
        search_type=req.search_type or "hybrid",
        collection_id=req.collection_id,
        limit=req.limit or 10
    )
    return APIResponse(success=True, data=res, message=f"Executed {req.search_type} search ({res.get('count')} results found)")


@router.get("/history", response_model=APIResponse[List[dict]])
async def get_search_history(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve search query trajectory history strictly filtered by user."""
    try:
        q = select(SearchHistory).where(SearchHistory.user_id == current_user.id).order_by(SearchHistory.created_at.desc()).limit(20)
        res = await db.execute(q)
        hist = res.scalars().all()
        return APIResponse(
            success=True,
            data=[
                {
                    "id": h.id,
                    "query": h.query,
                    "search_type": h.search_type,
                    "results_count": h.results_count,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in hist
            ],
            message="Search history loaded"
        )
    except Exception as e:
        logger.warning(f"Search history fetch error: {e}")
        return APIResponse(success=True, data=[], message="Search history empty")
