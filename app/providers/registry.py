from typing import Dict, List, Optional
from app.providers.base import BaseAIProvider
from app.providers.google_gemini import GeminiProvider
from app.providers.openai_claude import OpenAIProvider, ClaudeProvider
from app.providers.other_providers import (
    GroqProvider,
    DeepSeekProvider,
    MistralProvider,
    OpenRouterProvider,
    TogetherProvider,
    CohereProvider,
    XAIProvider,
    OllamaProvider,
    LMStudioProvider,
)
from app.logging.logger import logger

class ProviderRegistry:
    """Registry managing all 12 supported AI Providers & Model Routing Mappings"""

    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {}
        self._model_to_provider: Dict[str, str] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        defaults = [
            GeminiProvider(),
            OpenAIProvider(),
            ClaudeProvider(),
            GroqProvider(),
            DeepSeekProvider(),
            MistralProvider(),
            OpenRouterProvider(),
            TogetherProvider(),
            CohereProvider(),
            XAIProvider(),
            OllamaProvider(),
            LMStudioProvider(),
        ]
        for p in defaults:
            self.register_provider(p)

    def register_provider(self, provider: BaseAIProvider):
        self._providers[provider.provider_name] = provider
        for model in provider.supported_models:
            self._model_to_provider[model] = provider.provider_name
        logger.info(f"Registered AI Provider [{provider.provider_name}] with models: {provider.supported_models}")

    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        return self._providers.get(provider_name)

    def resolve_provider_for_model(self, model_name: str) -> Optional[BaseAIProvider]:
        provider_name = self._model_to_provider.get(model_name)
        if provider_name:
            return self._providers.get(provider_name)
        # Default fallback to Gemini if unknown model
        return self._providers.get("google_gemini")

    def list_all_providers(self) -> List[dict]:
        return [
            {
                "name": p.provider_name,
                "supported_models": p.supported_models,
            }
            for p in self._providers.values()
        ]

provider_registry = ProviderRegistry()
