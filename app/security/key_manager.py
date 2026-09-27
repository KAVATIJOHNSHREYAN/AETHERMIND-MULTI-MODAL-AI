import base64
import os
from cryptography.fernet import Fernet
from app.config.settings import settings
from app.logging.logger import logger

# Generate or derive symmetric Fernet key for API key encryption
KEY_SEED = (settings.CLERK_SECRET_KEY or "aethermind-enterprise-fernet-key-seed-32bytes!!").encode('utf-8')
FERNET_KEY = base64.urlsafe_b64encode(KEY_SEED[:32].ljust(32, b'0'))
cipher = Fernet(FERNET_KEY)

class APIKeyManager:
    """Enterprise API Key Manager for Encrypted Storage & Retrieval"""

    @staticmethod
    def encrypt_key(plain_key: str) -> str:
        if not plain_key:
            return ""
        return cipher.encrypt(plain_key.encode('utf-8')).decode('utf-8')

    @staticmethod
    def decrypt_key(encrypted_key: str) -> str:
        if not encrypted_key:
            return ""
        try:
            return cipher.decrypt(encrypted_key.encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"API key decryption failed: {str(e)}")
            return ""

    @staticmethod
    def mask_key(plain_key: str) -> str:
        if not plain_key or len(plain_key) < 8:
            return "********"
        return f"{plain_key[:4]}...{plain_key[-4:]}"
