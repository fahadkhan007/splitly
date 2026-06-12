from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import DB, CurrentUser
from app.models.expense import GroupExpense, GroupExpenseParticipant, DirectExpense
from app.models.user import User
from app.schemas.expense import (
    GroupExpenseCreate, GroupExpenseUpdate, GroupExpenseResponse,
    DirectExpenseCreate, DirectExpenseUpdate, DirectExpenseResponse,
)
from app.utils.balance import compute_participant_amounts, compute_direct_amount
from app.utils.email import send_expense_notification

router = APIRouter()


@router.post("/group", response_model=GroupExpenseResponse, status_code=201)
async def create_group_expense(body: GroupExpenseCreate, current_user: CurrentUser, db: DB):
    expense = GroupExpense(
        group_id=body.group_id,
        title=body.title,
        total_amount=body.total_amount,
        paid_by=body.paid_by,
        split_type=body.split_type,
        created_by=current_user.id,
    )
    db.add(expense)
    await db.flush()

    participant_data = [{"user_id": str(p.user_id), "share_value": p.share_value} for p in body.participants]
    computed = compute_participant_amounts(body.total_amount, body.split_type.value, participant_data)

    participant_emails = []
    for item in computed:
        db.add(GroupExpenseParticipant(
            expense_id=expense.id,
            user_id=UUID(item["user_id"]),
            share_value=item["share_value"],
            amount_owed=item["amount_owed"],
        ))
        user = (await db.execute(select(User).where(User.id == UUID(item["user_id"])))).scalar_one_or_none()
        if user:
            participant_emails.append(user.email)

    payer = (await db.execute(select(User).where(User.id == body.paid_by))).scalar_one_or_none()
    payer_name = payer.full_name if payer else "Someone"
    send_expense_notification(participant_emails, body.title, body.total_amount, payer_name)

    await db.flush()

    full_expense = (await db.execute(
        select(GroupExpense)
        .options(selectinload(GroupExpense.participants))
        .where(GroupExpense.id == expense.id)
    )).scalar_one()

    return full_expense


@router.put("/group/{expense_id}", response_model=GroupExpenseResponse)
async def update_group_expense(expense_id: UUID, body: GroupExpenseUpdate, current_user: CurrentUser, db: DB):
    expense = (await db.execute(select(GroupExpense).where(GroupExpense.id == expense_id))).scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can edit this expense")

    if body.title:
        expense.title = body.title
    if body.total_amount:
        expense.total_amount = body.total_amount
    if body.paid_by:
        expense.paid_by = body.paid_by
    if body.split_type:
        expense.split_type = body.split_type

    if body.participants:
        old_participants = (await db.execute(
            select(GroupExpenseParticipant).where(GroupExpenseParticipant.expense_id == expense_id)
        )).scalars().all()
        for p in old_participants:
            await db.delete(p)

        participant_data = [{"user_id": str(p.user_id), "share_value": p.share_value} for p in body.participants]
        computed = compute_participant_amounts(expense.total_amount, expense.split_type.value, participant_data)
        for item in computed:
            db.add(GroupExpenseParticipant(
                expense_id=expense_id,
                user_id=UUID(item["user_id"]),
                share_value=item["share_value"],
                amount_owed=item["amount_owed"],
            ))

    await db.flush()

    full_expense = (await db.execute(
        select(GroupExpense)
        .options(selectinload(GroupExpense.participants))
        .where(GroupExpense.id == expense_id)
    )).scalar_one()

    return full_expense


@router.delete("/group/{expense_id}", status_code=204)
async def delete_group_expense(expense_id: UUID, current_user: CurrentUser, db: DB):
    expense = (await db.execute(select(GroupExpense).where(GroupExpense.id == expense_id))).scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can delete this expense")
    await db.delete(expense)


@router.post("/direct", response_model=DirectExpenseResponse, status_code=201)
async def create_direct_expense(body: DirectExpenseCreate, current_user: CurrentUser, db: DB):
    amount_owed = compute_direct_amount(body.total_amount, body.split_type.value, body.share_value)

    expense = DirectExpense(
        title=body.title,
        total_amount=body.total_amount,
        paid_by=current_user.id,
        owed_by=body.owed_by,
        split_type=body.split_type,
        share_value=body.share_value,
        amount_owed=amount_owed,
        created_by=current_user.id,
    )
    db.add(expense)
    await db.flush()

    other_user = (await db.execute(select(User).where(User.id == body.owed_by))).scalar_one_or_none()
    if other_user:
        send_expense_notification([other_user.email, current_user.email], body.title, body.total_amount, current_user.full_name)

    return expense


@router.put("/direct/{expense_id}", response_model=DirectExpenseResponse)
async def update_direct_expense(expense_id: UUID, body: DirectExpenseUpdate, current_user: CurrentUser, db: DB):
    expense = (await db.execute(select(DirectExpense).where(DirectExpense.id == expense_id))).scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can edit this expense")

    if body.title:
        expense.title = body.title
    if body.total_amount:
        expense.total_amount = body.total_amount
    if body.split_type:
        expense.split_type = body.split_type
    if body.share_value is not None:
        expense.share_value = body.share_value

    expense.amount_owed = compute_direct_amount(
        float(expense.total_amount),
        expense.split_type.value,
        float(expense.share_value) if expense.share_value else None
    )

    return expense


@router.delete("/direct/{expense_id}", status_code=204)
async def delete_direct_expense(expense_id: UUID, current_user: CurrentUser, db: DB):
    expense = (await db.execute(select(DirectExpense).where(DirectExpense.id == expense_id))).scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the creator can delete this expense")
    await db.delete(expense)
