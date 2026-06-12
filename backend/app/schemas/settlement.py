from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SettlementCreate(BaseModel):
    payee_id: UUID
    amount_paid: float
    remark: str | None = None
    group_id: UUID | None = None


class SettlementResponse(BaseModel):
    id: UUID
    payer_id: UUID
    payee_id: UUID
    amount_paid: float
    remaining_amount: float
    remark: str | None
    group_id: UUID | None
    created_at: datetime

    class Config:
        from_attributes = True
