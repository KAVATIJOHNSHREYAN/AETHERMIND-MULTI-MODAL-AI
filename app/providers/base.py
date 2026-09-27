from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional

class BaseAIProvider(ABC):
    """Abstract Base Class for all Multimodal AI Providers"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique identifier name for provider"""
        pass

    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """List of model string identifiers supported by this provider"""
        pass

    @abstractmethod
    async def validate_api_key(self, api_key: str) -> bool:
        """Validate whether provided API key is active and valid"""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Check provider connectivity & API status"""
        pass

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: Optional[str] = None,
        **kwargs
    ) -> str:
        """Non-streaming response completion interface"""
        pass

    @abstractmethod
    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming response completion interface"""
        pass
