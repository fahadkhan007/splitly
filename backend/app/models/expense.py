from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group, GroupMember


class GroupExpense(Base):
    __tablename__ = "group_expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    paid_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="expenses")  # noqa: F821
    payer: Mapped["User"] = relationship("User", foreign_keys="[GroupExpense.paid_by]") #ignore
    creator: Mapped["User"] = relationship("User", foreign_keys="[GroupExpense.created_by]")
    participants: Mapped[list["GroupExpenseParticipant"]] = relationship(
        "GroupExpenseParticipant", back_populates="expense", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GroupExpense {self.title} — {self.total_amount}>"


class GroupExpenseParticipant(Base):
    __tablename__ = "group_expense_participants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("group_expenses.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount_owed: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Relationships
    expense: Mapped["GroupExpense"] = relationship(
        "GroupExpense", back_populates="participants"
    )
    user: Mapped["User"] = relationship("User")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Participant expense={self.expense_id} user={self.user_id} owes={self.amount_owed}>"


class DirectExpense(Base):
    __tablename__ = "direct_expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    paid_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount_owed: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    payer: Mapped["User"] = relationship("User", foreign_keys="[DirectExpense.paid_by]")
    debtor: Mapped["User"] = relationship("User", foreign_keys="[DirectExpense.owed_by]")
    creator: Mapped["User"] = relationship("User", foreign_keys="[DirectExpense.created_by]")

    def __repr__(self) -> str:
        return f"<DirectExpense {self.title} — {self.paid_by} → {self.owed_by}>"
