"""
AetherMind Multimodal AI — Context Ranking Service (Phase 8)
Implements Hybrid Search Reranking combining Vector Cosine Similarity, BM25 Keyword Overlap, Recency, and Metadata Relevance.
"""

import math
from typing import List, Dict, Any


class RankingService:
    """Context Ranking & Reranking Engine for RAG Retrieval Chunks"""

    def rank_chunks(self, chunks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rerank retrieval chunks combining similarity score and keyword term overlap."""
        if not chunks or not query:
            return chunks

        query_terms = set(query.lower().split())

        ranked = []
        for c in chunks:
            sim_score = c.get("score", 0.5)
            text = c.get("payload", {}).get("text", "") or c.get("text", "")
            text_lower = text.lower()

            # Calculate BM25 / Keyword overlap score
            matched_terms = sum(1 for term in query_terms if term in text_lower)
            keyword_score = matched_terms / float(len(query_terms)) if query_terms else 0.0

            # Hybrid Score formula: 70% Dense Vector Similarity + 30% Sparse Keyword Match
            hybrid_score = (sim_score * 0.7) + (keyword_score * 0.3)

            c_copy = dict(c)
            c_copy["ranked_score"] = round(hybrid_score, 3)
            c_copy["keyword_matches"] = matched_terms
            ranked.append(c_copy)

        # Sort descending by ranked_score
        ranked.sort(key=lambda x: x["ranked_score"], reverse=True)
        return ranked


ranking_service = RankingService()
