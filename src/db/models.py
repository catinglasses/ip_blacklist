from datetime import datetime

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from src.common.enums import IPStatus


class Base(DeclarativeBase):
    pass


class IPAddress(Base):
    __tablename__ = "ip_address"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    ip: Mapped[INET] = mapped_column(INET, nullable=False)
    status: Mapped[IPStatus] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ttl: Mapped[int] = mapped_column(Integer, nullable=True)  # in days, ge=1 le=365

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_blacklist_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("ip", name="uq_ip"),
        Index(
            "ix_ip_gist",
            ip,
            postgresql_using="gist",
            postgresql_ops={"ip": "inet_ops"},
        ),
    )
