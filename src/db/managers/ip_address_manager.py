from datetime import datetime
from typing import Any

from sqlalchemy import and_, delete, or_, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import func

from src.common.enums import IPStatus
from src.db.managers.base_manager import BaseDBManager
from src.db.models import IPAddress


class IPAddressDBManager(BaseDBManager):
    def __init__(self, async_engine: AsyncEngine) -> None:
        super().__init__(async_engine)

    async def upsert_ip_address(
        self,
        ip: str,
        status: IPStatus,
        ttl: int,
        description: str | None = None,
        created_at: datetime | None = None,
        last_blacklist_at: datetime | None = None,
        expires_at: datetime | None = None,
        current_session: AsyncSession | None = None,
    ) -> IPAddress | None:
        values: dict[str, Any] = {
            "ip": ip,
            "status": status.value if hasattr(status, "value") else status,
            'ttl': ttl,
            "description": description,
            "created_at": created_at,
            "last_blacklist_at": last_blacklist_at,
            "expires_at": expires_at,
        }

        values = {k: v for k, v in values.items() if v is not None}

        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            statement = (
                insert(IPAddress)
                .values(**values)
                .on_conflict_do_update(
                    index_elements=["ip"],
                    set_={
                        "status": values.get("status"),
                        'ttl': values.get('ttl'),
                        "description": values.get("description"),
                        "created_at": values.get("created_at"),
                        "last_blacklist_at": values.get("last_blacklist_at"),
                        "expires_at": values.get("expires_at"),
                        "updated_at": func.now(),
                    },
                )
                .returning(IPAddress)
            )
            return await session.scalar(statement=statement)

    async def get_ip_address(
        self,
        id: str | None = None,
        ip: str | None = None,
        for_update: bool = False,
        current_session: AsyncSession | None = None,
    ) -> IPAddress | None:
        if for_update and current_session is None:
            raise ValueError(
                "for_update=True requires having current_session for atomicity",
            )

        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            if id is not None:
                query = select(IPAddress).where(IPAddress.id == id)
            elif ip is not None:
                query = select(IPAddress).where(IPAddress.ip == ip)
            else:
                raise ValueError(
                    "Can't fetch ip_address without id or ip values being specified",
                )

            if for_update:
                query = query.with_for_update()

            return await session.scalar(query)

    async def get_blacklisted_ip_to_archive(
        self,
        cooling_period: int,
        current_session: AsyncSession | None = None,
    ) -> IPAddress | None:
        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            condition = and_(
                IPAddress.status == IPStatus.BLACKLIST.value,
                IPAddress.last_blacklist_at.is_not(None),
                IPAddress.ttl.is_not(None),
                IPAddress.last_blacklist_at + text(
                    f"interval '{cooling_period} days'",
                ) + func.cast(IPAddress.ttl, text) * text("interval '1 day'") <= func.now()
            )

            query = (
                select(IPAddress)
                .where(condition)
                .order_by(IPAddress.last_blacklist_at.asc())
                .limit(1)
                .with_for_update(skip_locked=True)
            )

            return await session.scalar(query)

    async def get_expired_ip_to_delete(
        self,
        current_session: AsyncSession | None = None,
    ) -> IPAddress | None:
        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            condition = and_(
                IPAddress.expires_at.is_not(None),
                IPAddress.expires_at <= func.now(),
                IPAddress.status == IPStatus.ARCHIVED.value,
            )

            query = (
                select(IPAddress)
                .where(condition)
                .order_by(IPAddress.expires_at.asc())
                .limit(1)
                .with_for_update(skip_locked=True)
            )

            return await session.scalar(query)

    async def get_all_ip_addresses(
        self,
        status: IPStatus | None = None,
        limit: int = 100,
        offset: int = 0,
        current_session: AsyncSession | None = None,
    ) -> list[IPAddress]:
        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            query = select(IPAddress).where(
                or_(
                    IPAddress.expires_at.is_(None),
                    IPAddress.expires_at > datetime.now(),
                ),
            )

            if status:
                query = query.where(IPAddress.status == status.value)

            query = query.order_by(IPAddress.created_at.desc())
            query = query.limit(limit).offset(offset)

            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_blacklisted_ip_addresses(
        self,
        current_session: AsyncSession | None = None,
    ) -> list[str]:
        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            query = select(IPAddress.ip).where(IPAddress.status == IPStatus.BLACKLIST)

            query = query.order_by(IPAddress.last_blacklist_at.desc())

            result = await session.execute(query)
            return [str(row[0]) for row in result.all()]

    async def patch_ip_address(
        self,
        id: str | None = None,
        ip: str | None = None,
        status: IPStatus | None = None,
        description: str | None = None,
        last_blacklist_at: datetime | None = None,
        expires_at: datetime | None = None,
        current_session: AsyncSession | None = None,
    ) -> IPAddress | None:
        update_data: dict[str, Any] = {}

        if status is not None:
            update_data["status"] = status.value if hasattr(status, "value") else status
        if description is not None:
            update_data["description"] = description
        if last_blacklist_at is not None:
            update_data["last_blacklist_at"] = last_blacklist_at
        if expires_at is not None:
            update_data["expires_at"] = expires_at

        if not update_data:
            return None

        update_data["updated_at"] = datetime.now()

        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            if id is not None:
                where_clause = IPAddress.id == id
            elif ip is not None:
                where_clause = IPAddress.ip == ip
            else:
                raise ValueError(
                    "Either id or ip must be specified to patch ip_address",
                )

            statement = (
                update(IPAddress)
                .where(where_clause)
                .values(**update_data)
                .returning(IPAddress)
            )

            result = await session.execute(statement)
            return result.scalar_one_or_none()

    async def delete_ip_address(
        self,
        id: str | None = None,
        ip: str | None = None,
        current_session: AsyncSession | None = None,
    ) -> None:
        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            if id is not None:
                query = delete(IPAddress).where(IPAddress.id == id)
            elif ip is not None:
                query = delete(IPAddress).where(IPAddress.ip == ip)
            else:
                raise ValueError(
                    "Can't delete ip_address without id or host values being specified",
                )

            await session.execute(query)

    async def bulk_add_ip_addresses(
        self,
        ip_addresses: list[dict[str, Any]],
        current_session: AsyncSession | None = None,
    ) -> list[IPAddress]:
        if not ip_addresses:
            return []

        async with self.use_or_create_session(
            current_session=current_session,
        ) as session:
            values: list[dict[str, Any]] = []
            for ip_data in ip_addresses:
                values.append(
                    {
                        "ip": ip_data["ip"],
                        "status": ip_data.get("status", IPStatus.BLACKLIST),
                        "description": ip_data.get("description"),
                        "last_blacklist_at": ip_data.get("last_blacklist_at"),
                        "expires_at": ip_data.get("expires_at"),
                    },
                )

            statement = (
                insert(IPAddress)
                .values(values)
                .on_conflict_do_update(
                    constraint="uq_ip",
                    set_={
                        "status": insert(IPAddress).excluded.status,
                        "description": insert(IPAddress).excluded.description,
                        "last_blacklist_at": insert(
                            IPAddress,
                        ).excluded.last_blacklist_at,
                        "expires_at": insert(IPAddress).excluded.expires_at,
                        "updated_at": func.now(),
                    },
                )
                .returning(IPAddress)
            )

            result = await session.execute(statement)
            return list(result.scalars().all())
