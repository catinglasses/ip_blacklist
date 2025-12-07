from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.common.enums import IPStatus
from src.common.schemas.ip_address import IPAddressBase


class IPAddressCreate(IPAddressBase):
    status: IPStatus = IPStatus.BLACKLIST
    ttl: int | None = Field(None, ge=1, le=365)  # in days


class IPAddressUpdate(BaseModel):
    description: str | None = None
    status: IPStatus | None = None
    expires_at: datetime | None = None


class IPAddressResponse(BaseModel):
    id: str
    status: IPStatus
    created_at: datetime
    updated_at: datetime
    last_blacklist_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class IPAddressesResponse(BaseModel):
    items: list[IPAddressResponse]
    total: int


class BlacklistResponse(BaseModel):
    ips: list[str]


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class ReactivateIPRequest(BaseModel):
    ip: str
    reason: str | None = None
