from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.error import ErrorResponse
from app.api.v1.schemas.operation import OperationRequest, OperationResponse
from app.api.v1.schemas.wallet import WalletResponse
from app.api.v1.services.transaction_service import TransactionService
from app.api.v1.services.wallet_service import WalletService
from app.core.database import get_db

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Получить баланс кошелька"
)
async def get_wallet(
        wallet_id: UUID,
        session: AsyncSession = Depends(get_db)
):
    wallet = await WalletService.get_wallet(session, wallet_id)

    return WalletResponse.from_orm(wallet)


@router.post(
    "/{wallet_id}/operation",
    response_model=OperationResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Выполнить операцию изменения баланса кошелька"
)
async def change_balance(
        wallet_id: UUID,
        request: OperationRequest,
        session: AsyncSession = Depends(get_db)
):
    result = await TransactionService.create_transaction(
        session, wallet_id, request.operation_type, request.amount, request.idempotency_key)

    return OperationResponse.from_orm(result)

@router.post(
    "/create-wallet",
    status_code=status.HTTP_201_CREATED,
    response_model=WalletResponse,
    summary="Создать кошелек"
)
async def create_wallet(session: AsyncSession = Depends(get_db)):
    wallet = await WalletService.create_wallet(session)

    return WalletResponse.from_orm(wallet)
