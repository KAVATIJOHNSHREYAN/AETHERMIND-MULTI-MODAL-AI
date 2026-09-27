from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.base import BaseAIProvider
from app.config.settings import settings
import httpx

class GeminiProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "google_gemini"

    @property
    def supported_models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-pro"]

    async def validate_api_key(self, api_key: str) -> bool:
        key = api_key or settings.GOOGLE_GEMINI_API_KEY
        return len(key) > 5

    async def health_check(self) -> dict:
        has_key = bool(settings.GOOGLE_GEMINI_API_KEY)
        return {
            "provider": self.provider_name,
            "status": "healthy" if has_key else "configured_without_key",
            "models_count": len(self.supported_models)
        }

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gemini-2.5-flash",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: Optional[str] = None,
        **kwargs
    ) -> str:
        return f"[Gemini {model} Response] AetherMind Provider Manager processed your request."

    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gemini-2.5-flash",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        chunks = ["[Gemini ", model, " Streaming] ", "AetherMind ", "Provider ", "Manager ", "Stream."]
        for chunk in chunks:
            yield chunk
