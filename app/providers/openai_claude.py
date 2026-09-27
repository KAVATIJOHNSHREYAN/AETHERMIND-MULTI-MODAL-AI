from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.base import BaseAIProvider
from app.config.settings import settings

class OpenAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> List[str]:
        return ["gpt-4.1", "gpt-4o", "gpt-4o-mini", "o1-preview", "gpt-3.5-turbo"]

    async def validate_api_key(self, api_key: str) -> bool:
        key = api_key or settings.OPENAI_API_KEY
        return len(key) > 5

    async def health_check(self) -> dict:
        has_key = bool(settings.OPENAI_API_KEY)
        return {"provider": self.provider_name, "status": "healthy" if has_key else "configured_without_key"}

    async def generate_response(self, messages: List[Dict[str, Any]], model: str = "gpt-4o", **kwargs) -> str:
        return f"[OpenAI {model} Response] AetherMind Provider Manager processed your request."

    async def stream_response(self, messages: List[Dict[str, Any]], model: str = "gpt-4o", **kwargs) -> AsyncGenerator[str, None]:
        for chunk in ["[OpenAI ", model, " Streaming] ", "Hello from OpenAI!"]:
            yield chunk

class ClaudeProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "anthropic_claude"

    @property
    def supported_models(self) -> List[str]:
        return ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"]

    async def validate_api_key(self, api_key: str) -> bool:
        key = api_key or settings.ANTHROPIC_API_KEY
        return len(key) > 5

    async def health_check(self) -> dict:
        has_key = bool(settings.ANTHROPIC_API_KEY)
        return {"provider": self.provider_name, "status": "healthy" if has_key else "configured_without_key"}

    async def generate_response(self, messages: List[Dict[str, Any]], model: str = "claude-3-5-sonnet", **kwargs) -> str:
        return f"[Claude {model} Response] AetherMind Provider Manager processed your request."

    async def stream_response(self, messages: List[Dict[str, Any]], model: str = "claude-3-5-sonnet", **kwargs) -> AsyncGenerator[str, None]:
        for chunk in ["[Claude ", model, " Streaming] ", "Hello from Anthropic!"]:
            yield chunk
