from typing import AsyncGenerator, Dict, Any, List, Optional
from app.providers.base import BaseAIProvider

class GroqProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "groq"
    @property
    def supported_models(self) -> List[str]: return ["groq-llama-3.3-70b", "groq-mixtral-8x7b"]
    async def validate_api_key(self, api_key: str) -> bool: return len(api_key or "") > 3
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "healthy"}
    async def generate_response(self, messages, model="groq-llama-3.3-70b", **kwargs) -> str: return f"[Groq {model} Response]"
    async def stream_response(self, messages, model="groq-llama-3.3-70b", **kwargs): yield f"[Groq {model} Stream]"

class DeepSeekProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "deepseek"
    @property
    def supported_models(self) -> List[str]: return ["deepseek-chat", "deepseek-reasoner-r1"]
    async def validate_api_key(self, api_key: str) -> bool: return len(api_key or "") > 3
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "healthy"}
    async def generate_response(self, messages, model="deepseek-chat", **kwargs) -> str: return f"[DeepSeek {model} Response]"
    async def stream_response(self, messages, model="deepseek-chat", **kwargs): yield f"[DeepSeek {model} Stream]"

class MistralProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "mistral"
    @property
    def supported_models(self) -> List[str]: return ["mistral-large", "mistral-small", "codestral"]
    async def validate_api_key(self, api_key: str) -> bool: return len(api_key or "") > 3
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "healthy"}
    async def generate_response(self, messages, model="mistral-large", **kwargs) -> str: return f"[Mistral {model} Response]"
    async def stream_response(self, messages, model="mistral-large", **kwargs): yield f"[Mistral {model} Stream]"

class OpenRouterProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "openrouter"
    @property
    def supported_models(self) -> List[str]: return ["openrouter-auto", "qwen-2.5-max"]
    async def validate_api_key(self, api_key: str) -> bool: return len(api_key or "") > 3
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "healthy"}
    async def generate_response(self, messages, model="openrouter-auto", **kwargs) -> str: return f"[OpenRouter {model} Response]"
    async def stream_response(self, messages, model="openrouter-auto", **kwargs): yield f"[OpenRouter {model} Stream]"

class TogetherProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "together"
    @property
    def supported_models(self) -> List[str]: return ["together-llama-3-70b"]
    async def validate_api_key(self, api_key: str) -> bool: return True
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "healthy"}
    async def generate_response(self, messages, model="together-llama-3-70b", **kwargs) -> str: return f"[Together {model} Response]"
    async def stream_response(self, messages, model="together-llama-3-70b", **kwargs): yield f"[Together {model} Stream]"

class CohereProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "cohere"
    @property
    def supported_models(self) -> List[str]: return ["command-r-plus"]
    async def validate_api_key(self, api_key: str) -> bool: return True
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "healthy"}
    async def generate_response(self, messages, model="command-r-plus", **kwargs) -> str: return f"[Cohere {model} Response]"
    async def stream_response(self, messages, model="command-r-plus", **kwargs): yield f"[Cohere {model} Stream]"

class XAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "xai"
    @property
    def supported_models(self) -> List[str]: return ["grok-2", "grok-vision-beta"]
    async def validate_api_key(self, api_key: str) -> bool: return True
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "healthy"}
    async def generate_response(self, messages, model="grok-2", **kwargs) -> str: return f"[xAI {model} Response]"
    async def stream_response(self, messages, model="grok-2", **kwargs): yield f"[xAI {model} Stream]"

class OllamaProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "ollama"
    @property
    def supported_models(self) -> List[str]: return ["ollama-llama3.2", "ollama-mistral", "ollama-phi4"]
    async def validate_api_key(self, api_key: str) -> bool: return True # Local does not require API key
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "local_ready", "endpoint": "http://localhost:11434"}
    async def generate_response(self, messages, model="ollama-llama3.2", **kwargs) -> str: return f"[Ollama Local {model} Response]"
    async def stream_response(self, messages, model="ollama-llama3.2", **kwargs): yield f"[Ollama Local {model} Stream]"

class LMStudioProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str: return "lmstudio"
    @property
    def supported_models(self) -> List[str]: return ["lmstudio-local-model"]
    async def validate_api_key(self, api_key: str) -> bool: return True
    async def health_check(self) -> dict: return {"provider": self.provider_name, "status": "local_ready", "endpoint": "http://localhost:1234"}
    async def generate_response(self, messages, model="lmstudio-local-model", **kwargs) -> str: return f"[LMStudio Local Response]"
    async def stream_response(self, messages, model="lmstudio-local-model", **kwargs): yield f"[LMStudio Local Stream]"
