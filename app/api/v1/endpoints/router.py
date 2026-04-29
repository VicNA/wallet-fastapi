from fastapi import APIRouter

from app.api.v1.endpoints.wallet_router import router as wallet_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(wallet_router)
