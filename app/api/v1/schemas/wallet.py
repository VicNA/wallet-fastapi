from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WalletResponse(BaseModel):
    wallet_id: UUID
    balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, wallet):
        return cls(
            wallet_id=wallet.id,
            balance=wallet.balance,
            created_at=wallet.created_at
        )
