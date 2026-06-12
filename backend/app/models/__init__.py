# Import all models here so Alembic can auto-detect them
from app.models.user import User
from app.models.friendship import Friendship, FriendshipStatus
from app.models.group import Group, GroupMember
from app.models.expense import GroupExpense, GroupExpenseParticipant, DirectExpense
from app.models.settlement import Settlement

__all__ = [
    "User",
    "Friendship",
    "FriendshipStatus",
    "Group",
    "GroupMember",
    "GroupExpense",
    "GroupExpenseParticipant",
    "DirectExpense",
    "Settlement",
]
