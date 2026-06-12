from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.friendship import Friendship
    from app.models.group import GroupMember

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    sent_friend_requests: Mapped[list["Friendship"]] = relationship(
        "Friendship", foreign_keys="Friendship.requester_id", back_populates="requester"
    )
    received_friend_requests: Mapped[list["Friendship"]] = relationship(
        "Friendship", foreign_keys="Friendship.addressee_id", back_populates="addressee"
    )
    group_memberships: Mapped[list["GroupMember"]] = relationship(
        "GroupMember", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
