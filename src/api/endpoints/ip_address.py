from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from src.api.exceptions import (
    BaseAPIException,
)
from src.api.schema import IPAddressCreate, IPAddressResponse
from src.bl.bl_manager import BLManager
from src.common.dependencies import get_bl_manager

router = APIRouter()


@router.post(
    "/add",
    response_model=IPAddressResponse,
)
async def add_ip_address(
    request: IPAddressCreate,
    bl_manager: BLManager = Depends(get_bl_manager),
) -> IPAddressResponse:
    try:
        return await bl_manager.ip_service.add_ip_address(ip_data=request)
    except BaseAPIException as e:
        raise e


@router.get(
    "/blacklist",
    response_class=PlainTextResponse,
)
async def get_blacklist(
    bl_manager: BLManager = Depends(get_bl_manager),
) -> str:
    ips = await bl_manager.ip_service.get_blacklisted_ips()
    return "\n".join(ips) + "\n" if ips else ""
