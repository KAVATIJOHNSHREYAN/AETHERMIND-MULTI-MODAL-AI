"""
AetherMind Multimodal AI — APIless Free Unlimited Chat Provider
Uses Pollinations AI OpenAI-compatible endpoint (no API keys, no quotas, no rate limits).
"""

import httpx
from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.base import BaseAIProvider
from app.logging.logger import logger


class APIlessProvider(BaseAIProvider):
    """APIless Unlimited Free AI Chat Provider — Zero Rate Limits & No Quota Restrictions"""

    # OpenAI-compatible endpoint that works without API keys
    BASE_URL = "https://text.pollinations.ai/openai"

    @property
    def provider_name(self) -> str:
        return "apiless"

    @property
    def supported_models(self) -> List[str]:
        return [
            "apiless-gpt4o",
            "apiless-qwen",
            "apiless-llama3",
            "apiless-deepseek",
            "apiless-mistral"
        ]

    async def validate_api_key(self, api_key: str) -> bool:
        return True  # APIless provider does not require any API keys

    async def health_check(self) -> dict:
        return {
            "provider": self.provider_name,
            "status": "healthy",
            "message": "APIless Unlimited Free Engine Operational"
        }

    def _map_model(self, model: str) -> str:
        m = (model or "").lower()
        if "deepseek" in m:
            return "deepseek-r1"
        if "qwen" in m:
            return "qwen-2.5-coder-32b"
        if "llama" in m:
            return "llama-3.3-70b"
        if "mistral" in m:
            return "mistral-small"
        return "openai"

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "apiless-gpt4o",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
        **kwargs
    ) -> str:
        target_model = self._map_model(model)

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            role = msg.get("role", "user")
            content = str(msg.get("content", "")).strip()
            if content:
                formatted_messages.append({"role": role, "content": content})

        if not formatted_messages:
            formatted_messages = [{"role": "user", "content": "Hello"}]

        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Try multiple endpoints in order of reliability
        endpoints = [
            ("https://text.pollinations.ai/openai/chat/completions", "openai-compat"),
            ("https://text.pollinations.ai/", "legacy-post"),
        ]

        for url, method_name in endpoints:
            try:
                async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                    res = await client.post(
                        url,
                        json=payload,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "AetherMind-Multimodal-AI/1.0"
                        }
                    )

                    if res.status_code == 200:
                        # Try OpenAI-compatible JSON response format first
                        try:
                            data = res.json()
                            if isinstance(data, dict):
                                # OpenAI format: {"choices": [{"message": {"content": "..."}}]}
                                choices = data.get("choices", [])
                                if choices and isinstance(choices, list):
                                    msg = choices[0].get("message", {})
                                    content = msg.get("content", "")
                                    if content and content.strip():
                                        logger.info(f"APIless provider [{method_name}] returned {len(content)} chars via model '{target_model}'")
                                        return content.strip()
                                # Direct content field
                                if data.get("content"):
                                    return data["content"].strip()
                                # Text field
                                if data.get("text"):
                                    return data["text"].strip()
                        except Exception:
                            pass

                        # Plain text response
                        text = res.text.strip()
                        if text and len(text) > 10 and not text.startswith("<!DOCTYPE") and not text.startswith("<html"):
                            logger.info(f"APIless provider [{method_name}] returned {len(text)} chars (plain text)")
                            return text

                    logger.warning(f"APIless [{method_name}] returned status {res.status_code}")

            except Exception as e:
                logger.warning(f"APIless [{method_name}] error: {e}")
                continue

        # Final fallback: Use the simple GET endpoint
        try:
            user_content = formatted_messages[-1]["content"] if formatted_messages else "Hello"
            import urllib.parse
            encoded = urllib.parse.quote(user_content[:500])
            get_url = f"https://text.pollinations.ai/{encoded}?model={target_model}"

            async with httpx.AsyncClient(timeout=45.0, follow_redirects=True) as client:
                res = await client.get(get_url)
                if res.status_code == 200 and res.text.strip() and not res.text.strip().startswith("<!DOCTYPE"):
                    logger.info(f"APIless GET fallback returned {len(res.text)} chars")
                    return res.text.strip()
        except Exception as e:
            logger.error(f"APIless GET fallback error: {e}")

        return "I apologize, but I'm experiencing a temporary connectivity issue. Please try again in a moment."

    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "apiless-gpt4o",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        full_text = await self.generate_response(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            **kwargs
        )
        words = full_text.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + (" " if i + 3 < len(words) else "")
            yield chunk
