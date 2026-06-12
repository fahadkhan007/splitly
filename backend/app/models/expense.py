from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class SplitType(str, enum.Enum):
    equal = "equal"
    exact = "exact"
    percentage = "percentage"
    shares = "shares"


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
    split_type: Mapped[SplitType] = mapped_column(
        Enum(SplitType), nullable=False, default=SplitType.equal
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
    group: Mapped["Group"] = relationship("Group", back_populates="expenses")
    payer: Mapped["User"] = relationship("User", foreign_keys="[GroupExpense.paid_by]")
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
    # For percentage: stores the % value (e.g. 40.00)
    # For shares: stores the share count (e.g. 2)
    # Null for equal and exact splits
    share_value: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    amount_owed: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Relationships
    expense: Mapped["GroupExpense"] = relationship(
        "GroupExpense", back_populates="participants"
    )
    user: Mapped["User"] = relationship("User")

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
    split_type: Mapped[SplitType] = mapped_column(
        Enum(SplitType), nullable=False, default=SplitType.equal
    )
    # % or share count for the owed_by person; null for equal/exact
    share_value: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
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
