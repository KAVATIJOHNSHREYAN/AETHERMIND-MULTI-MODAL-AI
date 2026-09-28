import httpx
import json
from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.base import BaseAIProvider
from app.config.settings import settings
from app.logging.logger import logger

class GeminiProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "google_gemini"

    @property
    def supported_models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

    async def validate_api_key(self, api_key: str) -> bool:
        key = api_key or settings.GOOGLE_GEMINI_API_KEY
        return bool(key and len(key) > 5)

    async def health_check(self) -> dict:
        has_key = bool(settings.GOOGLE_GEMINI_API_KEY)
        return {
            "provider": self.provider_name,
            "status": "healthy" if has_key else "configured_without_key",
            "models_count": len(self.supported_models)
        }

    def _normalize_model(self, model_name: str) -> str:
        m = (model_name or "").lower().strip()
        if "2.5" in m or "2.0" in m or "flash" in m:
            return "gemini-2.5-flash"
        if "pro" in m:
            return "gemini-2.5-pro"
        return "gemini-1.5-flash"

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
        key = api_key or settings.GOOGLE_GEMINI_API_KEY
        if not key:
            return "Google Gemini API key is missing. Please set GOOGLE_GEMINI_API_KEY in environment variables."

        target_model = self._normalize_model(model)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={key}"

        contents = []
        for msg in messages:
            r = msg.get("role", "user")
            role = "user" if r in ["user", "human"] else "model"
            parts = []

            # Check for inline image attachments
            if msg.get("attachments"):
                for att in msg.get("attachments", []):
                    if att.get("image_b64"):
                        parts.append({
                            "inlineData": {
                                "mimeType": att.get("mime_type") or "image/png",
                                "data": att.get("image_b64")
                            }
                        })

            txt = str(msg.get("content", "")).strip()
            if txt:
                parts.append({"text": txt})

            if parts:
                contents.append({
                    "role": role,
                    "parts": parts
                })

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        headers = {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text_chunks = [p.get("text", "") for p in parts if "text" in p]
                        if text_chunks:
                            return "".join(text_chunks)

                logger.warning(f"Gemini API primary call returned status {res.status_code}: {res.text[:200]}. Trying fallback.")
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                fallback_res = await client.post(fallback_url, json=payload, headers=headers)
                if fallback_res.status_code == 200:
                    data = fallback_res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text_chunks = [p.get("text", "") for p in parts if "text" in p]
                        if text_chunks:
                            return "".join(text_chunks)

                return f"Google Gemini API error ({res.status_code}): {res.text[:300]}"

        except Exception as e:
            logger.error(f"Gemini Provider execution error: {e}")
            return f"Unable to reach Google Gemini service: {str(e)}"

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
