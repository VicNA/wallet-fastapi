from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.common.enums import OperationType
from app.api.v1.common.utils import backoff
from app.api.v1.handlers.exceptions import OptimisticLockException
from app.api.v1.models.transaction import Transaction
from app.api.v1.services.wallet_service import WalletService

MAX_RETRIES = 5


class TransactionService:

    @staticmethod
    async def get_transaction(
            session: AsyncSession,
            wallet_id: UUID,
            key: UUID
    ) -> Transaction | None:
        """Получить транзакцию"""

        result = await session.execute(
            select(Transaction)
            .where(
                Transaction.wallet_id == wallet_id,
                Transaction.idempotency_key == key
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def create_transaction(
            session: AsyncSession,
            wallet_id: UUID,
            op_type: OperationType,
            amount: Decimal,
            key: UUID
    ) -> Transaction | None:
        """Создать новую транзакцю изменения баланса кошелька"""

        for attempt in range(MAX_RETRIES):
            try:
                if not session.in_transaction:
                    async with session.begin():
                        transaction = await TransactionService._create_transaction(
                            session, wallet_id, op_type, amount, key
                        )
                    await session.refresh(transaction)
                    return transaction
                else:
                    transaction = await TransactionService._create_transaction(
                        session, wallet_id, op_type, amount, key
                    )
                    await session.flush()
                    return transaction

            except OptimisticLockException:
                if attempt == MAX_RETRIES - 1:
                    raise
                await backoff(attempt)

        raise OptimisticLockException("Concurrent modification detected")

    @staticmethod
    async def _create_transaction(
            session: AsyncSession,
            wallet_id: UUID,
            op_type: OperationType,
            amount: Decimal,
            key: UUID
    ) -> Transaction:
        transaction = await TransactionService.get_transaction(session, wallet_id, key)
        if transaction:
            return transaction

        await WalletService.update_balance(session, wallet_id, op_type, amount)

        transaction = Transaction(
            wallet_id=wallet_id,
            amount=amount,
            operation_type=op_type,
            idempotency_key=key,
        )
        session.add(transaction)

        return transaction
