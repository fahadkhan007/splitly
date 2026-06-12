from fastapi import APIRouter, HTTPException

from app.core.dependencies import DB, CurrentUser
from app.schemas.user import UserResponse, UpdateProfileRequest
from app.schemas.chat import BalanceResponse
from app.models.friendship import Friendship, FriendshipStatus
from app.models.user import User
from app.utils.balance import get_net_balance
from sqlalchemy import select, or_

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: CurrentUser):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(body: UpdateProfileRequest, current_user: CurrentUser, db: DB):
    if body.full_name:
        current_user.full_name = body.full_name
    return current_user


@router.get("/me/balances", response_model=list[BalanceResponse])
async def get_all_balances(current_user: CurrentUser, db: DB):
    friendships = (await db.execute(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.accepted,
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.addressee_id == current_user.id
            )
        )
    )).scalars().all()

    balances = []
    for friendship in friendships:
        friend_id = friendship.addressee_id if friendship.requester_id == current_user.id else friendship.requester_id
        friend = (await db.execute(select(User).where(User.id == friend_id))).scalar_one_or_none()
        if not friend:
            continue

        net = await get_net_balance(current_user.id, friend_id, db)
        balances.append(BalanceResponse(
            friend_id=friend_id,
            friend_name=friend.full_name,
            friend_email=friend.email,
            net_amount=abs(net),
            you_owe=net < 0,
        ))

    return balances
