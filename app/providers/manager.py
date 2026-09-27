from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.registry import provider_registry
from app.logging.logger import logger

class AIProviderManager:
    """Central AI Provider Manager — Orchestrates dynamic routing, failover, retries, and key validation"""

    def __init__(self):
        self.registry = provider_registry

    async def generate(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        retries: int = 2,
        **kwargs
    ) -> str:
        """Route request to appropriate provider with automatic retry & failover"""
        provider = self.registry.resolve_provider_for_model(model)
        if not provider:
            # Automatic Failover to default Gemini provider
            provider = self.registry.get_provider("google_gemini")

        for attempt in range(retries + 1):
            try:
                logger.info(f"Dispatching AI request to provider [{provider.provider_name}] for model [{model}] (Attempt {attempt+1})")
                return await provider.generate_response(
                    messages=messages,
                    model=model,
                    system_prompt=system_prompt,
                    api_key=api_key,
                    **kwargs
                )
            except Exception as e:
                logger.warning(f"AI Provider [{provider.provider_name}] attempt {attempt+1} failed: {str(e)}")
                if attempt == retries:
                    # Final Failover to Gemini fallback
                    fallback = self.registry.get_provider("google_gemini")
                    if fallback and fallback != provider:
                        logger.info("Triggering automatic failover to fallback provider [google_gemini]")
                        return await fallback.generate_response(messages=messages, model="gemini-2.5-flash", **kwargs)
                    raise e

    async def stream(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Route streaming request to appropriate provider"""
        provider = self.registry.resolve_provider_for_model(model)
        if not provider:
            provider = self.registry.get_provider("google_gemini")

        async for chunk in provider.stream_response(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            api_key=api_key,
            **kwargs
        ):
            yield chunk

    async def test_provider_connection(self, provider_name: str, api_key: str) -> dict:
        """Test provider connectivity and API key validity"""
        provider = self.registry.get_provider(provider_name)
        if not provider:
            return {"success": False, "provider": provider_name, "message": f"Provider '{provider_name}' not registered"}

        is_valid = await provider.validate_api_key(api_key)
        health = await provider.health_check()
        return {
            "success": is_valid,
            "provider": provider_name,
            "valid_key": is_valid,
            "health": health
        }

ai_provider_manager = AIProviderManager()
