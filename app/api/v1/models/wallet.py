import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, CheckConstraint, DateTime, Integer, func, Index, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_wallet_version", "id", "version"),
        CheckConstraint('balance >= 0', name='check_balance_non_negative'),
    )
