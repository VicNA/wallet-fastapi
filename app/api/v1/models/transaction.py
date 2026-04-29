import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, Enum, Index, UniqueConstraint, DateTime, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.api.v1.common.enums import OperationType
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("wallets.id"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    operation_type: Mapped[OperationType] = mapped_column(
        Enum(OperationType, name="operation_type"),
        nullable=False,
    )
    idempotency_key: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    __table_args__ = (
        Index("ix_transactions_wallet_id", "wallet_id"),
        UniqueConstraint("wallet_id", "idempotency_key", name="uq_wallet_idempotency"),
    )
