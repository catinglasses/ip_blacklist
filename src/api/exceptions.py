from typing import Any, Dict

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,  # noqa: ANN401
        headers: Dict[str, str] | None = None,
        error_code: str | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class IPValidationException(BaseAPIException):
    def __init__(
        self,
        detail: str = "Invalid IP-address",
        error_code: str = "INVALID_IP",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
        )


class PrivateIPException(IPValidationException):
    def __init__(self) -> None:
        super().__init__(
            detail="Private IPs are disallowed",
            error_code="PRIVATE_IP",
        )


class DuplicateIPException(BaseAPIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="IP address already exists",
            error_code="DUPLICATE_IP",
        )


class IPNotFoundException(BaseAPIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP address not found",
            error_code="IP_NOT_FOUND",
        )


class InvalidTTLException(BaseAPIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TTL must be >=1 and <=365 days",
            error_code="INVALID_TTL",
        )
