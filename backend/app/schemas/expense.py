from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.expense import SplitType


class ParticipantInput(BaseModel):
    user_id: UUID
    share_value: float | None = None


class GroupExpenseCreate(BaseModel):
    title: str
    total_amount: float
    paid_by: UUID
    split_type: SplitType
    participants: list[ParticipantInput]


class GroupExpenseUpdate(BaseModel):
    title: str | None = None
    total_amount: float | None = None
    paid_by: UUID | None = None
    split_type: SplitType | None = None
    participants: list[ParticipantInput] | None = None


class DirectExpenseCreate(BaseModel):
    title: str
    total_amount: float
    owed_by: UUID
    split_type: SplitType
    share_value: float | None = None


class DirectExpenseUpdate(BaseModel):
    title: str | None = None
    total_amount: float | None = None
    split_type: SplitType | None = None
    share_value: float | None = None


class ParticipantResponse(BaseModel):
    user_id: UUID
    share_value: float | None
    amount_owed: float

    class Config:
        from_attributes = True


class GroupExpenseResponse(BaseModel):
    id: UUID
    group_id: UUID
    title: str
    total_amount: float
    paid_by: UUID
    split_type: SplitType
    created_by: UUID
    created_at: datetime
    participants: list[ParticipantResponse]

    class Config:
        from_attributes = True


class DirectExpenseResponse(BaseModel):
    id: UUID
    title: str
    total_amount: float
    paid_by: UUID
    owed_by: UUID
    split_type: SplitType
    share_value: float | None
    amount_owed: float
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True
