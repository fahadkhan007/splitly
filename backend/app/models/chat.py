from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ExpenseType(str, enum.Enum):
    group = "group"
    direct = "direct"


class ExpenseMessage(Base):
    __tablename__ = "expense_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
        # No FK — points to either group_expenses or direct_expenses based on expense_type
    )
    expense_type: Mapped[ExpenseType] = mapped_column(
        Enum(ExpenseType), nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    sender: Mapped["User"] = relationship("User", foreign_keys="[ExpenseMessage.sender_id]")

    def __repr__(self) -> str:
        return f"<ExpenseMessage {self.expense_type}:{self.expense_id} from={self.sender_id}>"
