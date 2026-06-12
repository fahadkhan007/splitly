from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    payee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount_paid: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    remaining_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    payer: Mapped["User"] = relationship("User", foreign_keys="[Settlement.payer_id]")
    payee: Mapped["User"] = relationship("User", foreign_keys="[Settlement.payee_id]")
    group: Mapped["Group"] = relationship("Group", foreign_keys="[Settlement.group_id]")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Settlement payer={self.payer_id} payee={self.payee_id} amount={self.amount_paid}>"
