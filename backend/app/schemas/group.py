from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    member_ids: list[UUID]


class AddMemberRequest(BaseModel):
    user_id: UUID


class MemberResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: str

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class GroupDetailResponse(BaseModel):
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime
    members: list[MemberResponse]

    class Config:
        from_attributes = True
