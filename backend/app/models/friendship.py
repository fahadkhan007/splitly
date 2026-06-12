from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class FriendshipStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"


class Friendship(Base):
    __tablename__ = "friendships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    addressee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[FriendshipStatus] = mapped_column(
        Enum(FriendshipStatus), default=FriendshipStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    requester: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys="[Friendship.requester_id]", back_populates="sent_friend_requests"
    )
    addressee: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys="[Friendship.addressee_id]", back_populates="received_friend_requests"
    )

    def __repr__(self) -> str:
        return f"<Friendship {self.requester_id} → {self.addressee_id} [{self.status}]>"
