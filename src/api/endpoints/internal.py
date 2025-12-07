from fastapi import APIRouter, Depends, Header, HTTPException, status

import settings
from src.api.exceptions import BaseAPIException
from src.api.schema import IPAddressResponse, ReactivateIPRequest
from src.bl.bl_manager import BLManager
from src.common.dependencies import get_bl_manager

router = APIRouter()


async def verify_internal_token(
    api_token: str = Header(..., alias="X-Internal-Token"),
) -> None:
    expected_token = settings.INTERNAL_API_TOKEN

    if api_token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )


@router.post(
    "/reactivate",
    response_model=IPAddressResponse,
    dependencies=[Depends(verify_internal_token)],
)
async def reactivate_ip(
    request: ReactivateIPRequest,
    bl_manager: BLManager = Depends(get_bl_manager),
) -> IPAddressResponse:
    try:
        return await bl_manager.ip_service.reblacklist_ip(
            ip=request.ip,
            reason=request.reason,
        )
    except BaseAPIException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )
