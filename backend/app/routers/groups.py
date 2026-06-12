from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.dependencies import DB, CurrentUser
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate, GroupResponse, GroupDetailResponse, AddMemberRequest, MemberResponse

router = APIRouter()


@router.get("/", response_model=list[GroupResponse])
async def list_groups(current_user: CurrentUser, db: DB):
    memberships = (await db.execute(
        select(GroupMember).where(GroupMember.user_id == current_user.id)
    )).scalars().all()

    group_ids = [m.group_id for m in memberships]
    groups = (await db.execute(select(Group).where(Group.id.in_(group_ids)))).scalars().all()
    return groups


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(body: GroupCreate, current_user: CurrentUser, db: DB):
    group = Group(name=body.name, created_by=current_user.id)
    db.add(group)
    await db.flush()

    all_member_ids = list(set([current_user.id] + body.member_ids))
    for user_id in all_member_ids:
        db.add(GroupMember(group_id=group.id, user_id=user_id))

    return group


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group(group_id: UUID, current_user: CurrentUser, db: DB):
    group = (await db.execute(select(Group).where(Group.id == group_id))).scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = (await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        )
    )).scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    members_rows = (await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id)
    )).scalars().all()

    member_details = []
    for row in members_rows:
        user = (await db.execute(select(User).where(User.id == row.user_id))).scalar_one_or_none()
        if user:
            member_details.append(MemberResponse(
                user_id=row.user_id,
                full_name=user.full_name,
                email=user.email
            ))

    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        created_by=group.created_by,
        created_at=group.created_at,
        members=member_details
    )


@router.post("/{group_id}/members", status_code=201)
async def add_member(group_id: UUID, body: AddMemberRequest, current_user: CurrentUser, db: DB):
    group = (await db.execute(select(Group).where(Group.id == group_id))).scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    existing = (await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == body.user_id
        )
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    db.add(GroupMember(group_id=group_id, user_id=body.user_id))
    return {"message": "Member added"}


@router.delete("/{group_id}/members/{user_id}")
async def remove_member(group_id: UUID, user_id: UUID, current_user: CurrentUser, db: DB):
    group = (await db.execute(select(Group).where(Group.id == group_id))).scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    membership = (await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    )).scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    await db.delete(membership)
    return {"message": "Member removed"}
