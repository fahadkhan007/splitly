from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageCreate(BaseModel):
    message: str


class MessageResponse(BaseModel):
    id: UUID
    expense_id: UUID
    expense_type: str
    sender_id: UUID
    sender_name: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    friend_id: UUID
    friend_name: str
    friend_email: str
    net_amount: float
    you_owe: bool
