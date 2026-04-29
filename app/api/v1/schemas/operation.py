from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.api.v1.common.enums import OperationType


class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(
        ...,
        gt=Decimal('0'),
        max_digits=18,
        decimal_places=2,
        description="Сумма операции должна быть больше нуля"
    )
    idempotency_key: UUID


class OperationResponse(BaseModel):
    transaction_id: UUID
    wallet_id: UUID
    operation_type: OperationType
    amount: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, transaction):
        return cls(
            transaction_id=transaction.id,
            wallet_id=transaction.wallet_id,
            operation_type=transaction.operation_type,
            amount=transaction.amount,
            status="SUCCESS",
        )
