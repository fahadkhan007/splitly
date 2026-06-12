# Import all models here so Alembic can auto-detect them
from app.models.user import User
from app.models.friendship import Friendship, FriendshipStatus
from app.models.group import Group, GroupMember
from app.models.expense import GroupExpense, GroupExpenseParticipant, DirectExpense, SplitType
from app.models.settlement import Settlement
from app.models.chat import ExpenseMessage, ExpenseType

__all__ = [
    "User",
    "Friendship",
    "FriendshipStatus",
    "Group",
    "GroupMember",
    "GroupExpense",
    "GroupExpenseParticipant",
    "DirectExpense",
    "SplitType",
    "Settlement",
    "ExpenseMessage",
    "ExpenseType",
]
