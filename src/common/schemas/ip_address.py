from datetime import datetime
from ipaddress import ip_address

from pydantic import BaseModel, field_validator


class IPAddressBase(BaseModel):
    ip: str
    description: str | None = None
    expires_at: datetime | None = None

    @field_validator("ip")
    def validate_ip_address(cls, v: str) -> str:  # noqa: N805
        try:
            ip = ip_address(address=v)
            if ip.is_private:
                raise ValueError("Private IPs are disallowed")
            return str(ip)
        except ValueError as e:
            raise ValueError(f"Invalid IP address: {e}")
