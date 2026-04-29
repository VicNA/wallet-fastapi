import uuid
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.common.enums import OperationType
from app.api.v1.handlers.exceptions import WalletNotFound, OptimisticLockException, WalletNotEnoughFunds
from app.api.v1.models.wallet import Wallet


class WalletService:

    @staticmethod
    async def get_wallet(session: AsyncSession, wallet_id: UUID) -> Wallet:
        """Получение текущего баланса кошелька."""

        result = await session.execute(
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update(nowait=True)
        )

        wallet = result.scalar_one_or_none()
        if not wallet:
            raise WalletNotFound(f"Wallet with id {wallet_id} not found")

        return wallet

    @staticmethod
    async def update_balance(
            session: AsyncSession,
            wallet_id: UUID,
            op_type: OperationType,
            amount: Decimal,
    ) -> Wallet:
        """Изменить баланс кошелька"""

        wallet = await WalletService.get_wallet(session, wallet_id)

        new_balance = wallet.balance

        if op_type == OperationType.DEPOSIT:
            new_balance += amount
        elif op_type == OperationType.WITHDRAW:
            if wallet.balance < amount:
                raise WalletNotEnoughFunds("Недостаточно средств")
            new_balance -= amount

        wallet = await WalletService.__update_wallet(session, wallet_id, new_balance, wallet.version)
        if not wallet:
            raise OptimisticLockException("Concurrent modification detected")

        return wallet

    @staticmethod
    async def create_wallet(session: AsyncSession) -> Wallet | None:
        """Создать новый кошелек"""

        wallet_id = uuid.uuid4()
        wallet = Wallet(id=wallet_id)

        session.add(wallet)
        try:
            await session.flush()
            await session.refresh(wallet)
            return wallet
        except IntegrityError:
            existing = await WalletService.get_wallet(session, wallet_id)
            if existing:
                return existing
            raise


    @staticmethod
    async def __update_wallet(
            session: AsyncSession,
            wallet_id: UUID,
            new_balance: Decimal,
            version: int
    ) -> Wallet | None:
        """Сохранить изменения баланса кошелька"""

        stmt = (
            update(Wallet)
            .where(
                Wallet.id == wallet_id,
                Wallet.version == version
            )
            .values(
                balance=new_balance,
                version=version + 1
            )
            .returning(Wallet.id)
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()
