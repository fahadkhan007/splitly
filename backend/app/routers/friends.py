from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, or_

from app.core.config import settings
from app.core.dependencies import DB, CurrentUser
from app.core.security import create_email_token
from app.models.friendship import Friendship, FriendshipStatus
from app.models.user import User
from app.schemas.friendship import InviteFriendRequest, FriendResponse, FriendshipResponse
from app.schemas.chat import BalanceResponse
from app.utils.balance import get_net_balance
from app.utils.email import send_invite_email

router = APIRouter()


@router.get("/", response_model=list[FriendResponse])
async def list_friends(current_user: CurrentUser, db: DB):
    friendships = (await db.execute(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.accepted,
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.addressee_id == current_user.id
            )
        )
    )).scalars().all()

    friend_ids = [
        f.addressee_id if f.requester_id == current_user.id else f.requester_id
        for f in friendships
    ]

    friends = (await db.execute(select(User).where(User.id.in_(friend_ids)))).scalars().all()
    return friends


@router.get("/pending", response_model=list[FriendshipResponse])
async def list_pending(current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Friendship).where(
            Friendship.addressee_id == current_user.id,
            Friendship.status == FriendshipStatus.pending
        )
    )
    return result.scalars().all()


@router.post("/invite")
async def invite_friend(body: InviteFriendRequest, current_user: CurrentUser, db: DB):
    if body.email == current_user.email:
        raise HTTPException(status_code=400, detail="You cannot invite yourself")

    invitee = (await db.execute(select(User).where(User.email == body.email))).scalar_one_or_none()

    if invitee:
        existing = (await db.execute(
            select(Friendship).where(
                or_(
                    (Friendship.requester_id == current_user.id) & (Friendship.addressee_id == invitee.id),
                    (Friendship.requester_id == invitee.id) & (Friendship.addressee_id == current_user.id)
                )
            )
        )).scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="Friend request already exists")

        friendship = Friendship(requester_id=current_user.id, addressee_id=invitee.id)
        db.add(friendship)

    token = create_email_token(body.email)
    invite_url = f"{settings.FRONTEND_URL}/register?invite_token={token}&email={body.email}"
    send_invite_email(body.email, current_user.full_name, invite_url)

    return {"message": "Invite sent"}


@router.post("/{friendship_id}/accept")
async def accept_friend(friendship_id: UUID, current_user: CurrentUser, db: DB):
    friendship = (await db.execute(
        select(Friendship).where(
            Friendship.id == friendship_id,
            Friendship.addressee_id == current_user.id,
            Friendship.status == FriendshipStatus.pending
        )
    )).scalar_one_or_none()

    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")

    friendship.status = FriendshipStatus.accepted
    return {"message": "Friend request accepted"}


@router.get("/{friend_id}/balance", response_model=BalanceResponse)
async def get_friend_balance(friend_id: UUID, current_user: CurrentUser, db: DB):
    friend = (await db.execute(select(User).where(User.id == friend_id))).scalar_one_or_none()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    net = await get_net_balance(current_user.id, friend_id, db)
    return BalanceResponse(
        friend_id=friend_id,
        friend_name=friend.full_name,
        friend_email=friend.email,
        net_amount=abs(net),
        you_owe=net < 0,
    )
