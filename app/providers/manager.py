from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.registry import provider_registry
from app.logging.logger import logger

class AIProviderManager:
    """Central AI Provider Manager — Orchestrates dynamic routing, failover, retries, and key validation"""

    def __init__(self):
        self.registry = provider_registry

    def _determine_best_provider(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ):
        """Smart Auto Routing:
        - Pure text chat -> APIless Unlimited Engine (zero API key, zero rate limits)
        - Attachments / Images / Vision -> Official Multimodal API (Google Gemini / OpenAI Vision)
        """
        has_attachments = kwargs.get("has_attachments", False)
        if not has_attachments and messages:
            for m in messages:
                if isinstance(m, dict):
                    if m.get("attachments") or "ATTACHED MEDIA" in str(m.get("content", "")) or "[ATTACHED MEDIA" in str(m.get("content", "")):
                        has_attachments = True
                        break

        if model in ("auto", "aethermind-auto", "default"):
            if has_attachments:
                provider = self.registry.get_provider("google_gemini")
                target_model = "gemini-2.5-flash"
            else:
                provider = self.registry.get_provider("apiless")
                target_model = "apiless-gpt4o"
            
            if provider:
                return provider, target_model

        provider = self.registry.resolve_provider_for_model(model)
        if not provider:
            if has_attachments:
                provider = self.registry.get_provider("google_gemini") or self.registry.get_provider("apiless")
            else:
                provider = self.registry.get_provider("apiless") or self.registry.get_provider("google_gemini")

        return provider, model

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
        provider, target_model = self._determine_best_provider(model, messages, **kwargs)

        for attempt in range(retries + 1):
            try:
                logger.info(f"Dispatching AI request to provider [{provider.provider_name}] for model [{target_model}] (Attempt {attempt+1})")
                res = await provider.generate_response(
                    messages=messages,
                    model=target_model,
                    system_prompt=system_prompt,
                    api_key=api_key,
                    **kwargs
                )
                if res and not res.startswith("Google Gemini API error (429)") and not "RESOURCE_EXHAUSTED" in res and not "rate limit" in res.lower():
                    return res
                raise RuntimeError(f"Provider returned error/rate limit: {res}")
            except Exception as e:
                logger.warning(f"AI Provider [{provider.provider_name}] attempt {attempt+1} failed: {str(e)}")
                if attempt == retries:
                    # Automatic Failover to APIless unlimited provider
                    apiless_fallback = self.registry.get_provider("apiless")
                    if apiless_fallback and apiless_fallback != provider:
                        logger.info("Triggering automatic failover to APIless Unlimited Engine")
                        return await apiless_fallback.generate_response(messages=messages, model="apiless-gpt4o", system_prompt=system_prompt, **kwargs)
                    return f"AetherMind AI Engine completion: {str(e)}"

    async def stream(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Route streaming request to appropriate provider with APIless fallback"""
        provider, target_model = self._determine_best_provider(model, messages, **kwargs)

        try:
            async for chunk in provider.stream_response(
                messages=messages,
                model=target_model,
                system_prompt=system_prompt,
                api_key=api_key,
                **kwargs
            ):
                yield chunk
        except Exception as stream_err:
            logger.warning(f"Streaming provider [{provider.provider_name}] failed: {stream_err}. Failing over to APIless Provider.")
            apiless = self.registry.get_provider("apiless")
            if apiless and apiless != provider:
                async for chunk in apiless.stream_response(
                    messages=messages,
                    model="apiless-gpt4o",
                    system_prompt=system_prompt,
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
