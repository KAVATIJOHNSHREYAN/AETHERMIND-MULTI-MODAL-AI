import httpx
from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.base import BaseAIProvider
from app.providers.google_gemini import GeminiProvider
from app.config.settings import settings
from app.logging.logger import logger

class OpenAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> List[str]:
        return ["gpt-4.1", "gpt-4o", "gpt-4o-mini", "o1-preview", "gpt-3.5-turbo"]

    async def validate_api_key(self, api_key: str) -> bool:
        key = api_key or settings.OPENAI_API_KEY
        return bool(key and len(key) > 5)

    async def health_check(self) -> dict:
        has_key = bool(settings.OPENAI_API_KEY)
        return {"provider": self.provider_name, "status": "healthy" if has_key else "configured_without_key"}

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-4o",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: Optional[str] = None,
        **kwargs
    ) -> str:
        key = api_key or settings.OPENAI_API_KEY
        if key and len(key) > 5:
            formatted_msgs = []
            if system_prompt:
                formatted_msgs.append({"role": "system", "content": system_prompt})
            for m in messages:
                formatted_msgs.append({"role": m.get("role", "user"), "content": str(m.get("content", ""))})

            target_model = "gpt-4o-mini" if "mini" in model or "3.5" in model else "gpt-4o"
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {"model": target_model, "messages": formatted_msgs, "temperature": temperature, "max_tokens": max_tokens}

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "")
            except Exception as e:
                logger.warning(f"OpenAI call failed ({e}). Routing to Gemini engine.")

        # Seamless fallback to Gemini AI Engine
        gemini_fallback = GeminiProvider()
        return await gemini_fallback.generate_response(messages=messages, model="gemini-2.5-flash", system_prompt=system_prompt)

    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-4o",
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        res_text = await self.generate_response(messages=messages, model=model, system_prompt=system_prompt, api_key=api_key, **kwargs)
        words = res_text.split(" ")
        for i in range(0, len(words), 3):
            yield " ".join(words[i:i+3]) + (" " if i + 3 < len(words) else "")


class ClaudeProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "anthropic_claude"

    @property
    def supported_models(self) -> List[str]:
        return ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"]

    async def validate_api_key(self, api_key: str) -> bool:
        key = api_key or settings.ANTHROPIC_API_KEY
        return bool(key and len(key) > 5)

    async def health_check(self) -> dict:
        has_key = bool(settings.ANTHROPIC_API_KEY)
        return {"provider": self.provider_name, "status": "healthy" if has_key else "configured_without_key"}

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "claude-3-5-sonnet",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        api_key: Optional[str] = None,
        **kwargs
    ) -> str:
        key = api_key or settings.ANTHROPIC_API_KEY
        if key and len(key) > 5:
            formatted_msgs = []
            for m in messages:
                role = "user" if m.get("role") in ["user", "human"] else "assistant"
                formatted_msgs.append({"role": role, "content": str(m.get("content", ""))})

            url = "https://api.anthropic.com/v1/messages"
            headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            payload = {"model": "claude-3-5-sonnet-20241022", "max_tokens": max_tokens, "messages": formatted_msgs}
            if system_prompt:
                payload["system"] = system_prompt

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        content_blocks = data.get("content", [])
                        if content_blocks:
                            return "".join([b.get("text", "") for b in content_blocks if b.get("type") == "text"])
            except Exception as e:
                logger.warning(f"Claude call failed ({e}). Routing to Gemini engine.")

        # Seamless fallback to Gemini AI Engine
        gemini_fallback = GeminiProvider()
        return await gemini_fallback.generate_response(messages=messages, model="gemini-2.5-flash", system_prompt=system_prompt)

    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "claude-3-5-sonnet",
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        res_text = await self.generate_response(messages=messages, model=model, system_prompt=system_prompt, api_key=api_key, **kwargs)
        words = res_text.split(" ")
        for i in range(0, len(words), 3):
            yield " ".join(words[i:i+3]) + (" " if i + 3 < len(words) else "")
