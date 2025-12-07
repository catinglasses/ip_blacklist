from fastapi import APIRouter

from src.api.endpoints.internal import router as internal_router
from src.api.endpoints.ip_address import router as ip_router

api_router = APIRouter()

api_router.include_router(internal_router, prefix="/internal", tags=["INTERNAL"])
api_router.include_router(ip_router, prefix="/ip", tags=["IP-ADDRS"])
