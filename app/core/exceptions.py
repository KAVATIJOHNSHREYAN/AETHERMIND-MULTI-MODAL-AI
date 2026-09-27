from fastapi import status

class BaseAppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class EntityNotFoundException(BaseAppException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with ID '{entity_id}' not found",
            code="ENTITY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

class ProviderException(BaseAppException):
    def __init__(self, provider_name: str, details: str):
        super().__init__(
            message=f"Provider [{provider_name}] error: {details}",
            code="PROVIDER_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY
        )
