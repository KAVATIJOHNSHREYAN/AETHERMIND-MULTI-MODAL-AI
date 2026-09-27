import hashlib
import hmac
import base64

class SecurityUtils:
    """Security utilities for API key masking, hashing, and token verification"""

    @staticmethod
    def mask_api_key(api_key: str) -> str:
        if not api_key or len(api_key) < 8:
            return "********"
        return f"{api_key[:4]}...{api_key[-4:]}"

    @staticmethod
    def hash_string(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
