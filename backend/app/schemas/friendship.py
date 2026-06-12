from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class InviteFriendRequest(BaseModel):
    email: EmailStr


class FriendResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True


class FriendshipResponse(BaseModel):
    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
