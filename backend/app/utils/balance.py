from uuid import UUID

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import DirectExpense, GroupExpense, GroupExpenseParticipant
from app.models.settlement import Settlement


async def get_net_balance(user_a: UUID, user_b: UUID, db: AsyncSession) -> float:
    a, b = str(user_a), str(user_b)

    direct_a_paid = await db.execute(
        select(DirectExpense).where(
            DirectExpense.paid_by == user_a,
            DirectExpense.owed_by == user_b
        )
    )
    owed_to_a = sum(float(e.amount_owed) for e in direct_a_paid.scalars())

    direct_b_paid = await db.execute(
        select(DirectExpense).where(
            DirectExpense.paid_by == user_b,
            DirectExpense.owed_by == user_a
        )
    )
    owed_to_b = sum(float(e.amount_owed) for e in direct_b_paid.scalars())

    group_expenses_a_paid = await db.execute(
        select(GroupExpense).where(GroupExpense.paid_by == user_a)
    )
    for expense in group_expenses_a_paid.scalars():
        participant = await db.execute(
            select(GroupExpenseParticipant).where(
                GroupExpenseParticipant.expense_id == expense.id,
                GroupExpenseParticipant.user_id == user_b
            )
        )
        row = participant.scalar_one_or_none()
        if row:
            owed_to_a += float(row.amount_owed)

    group_expenses_b_paid = await db.execute(
        select(GroupExpense).where(GroupExpense.paid_by == user_b)
    )
    for expense in group_expenses_b_paid.scalars():
        participant = await db.execute(
            select(GroupExpenseParticipant).where(
                GroupExpenseParticipant.expense_id == expense.id,
                GroupExpenseParticipant.user_id == user_a
            )
        )
        row = participant.scalar_one_or_none()
        if row:
            owed_to_b += float(row.amount_owed)

    settlements_b_to_a = await db.execute(
        select(Settlement).where(
            Settlement.payer_id == user_b,
            Settlement.payee_id == user_a
        )
    )
    settled_b_to_a = sum(float(s.amount_paid) for s in settlements_b_to_a.scalars())

    settlements_a_to_b = await db.execute(
        select(Settlement).where(
            Settlement.payer_id == user_a,
            Settlement.payee_id == user_b
        )
    )
    settled_a_to_b = sum(float(s.amount_paid) for s in settlements_a_to_b.scalars())

    return round(owed_to_a - owed_to_b - settled_b_to_a + settled_a_to_b, 2)


def compute_participant_amounts(total: float, split_type: str, participants: list[dict]) -> list[dict]:
    results = []

    if split_type == "equal":
        per_person = round(total / len(participants), 2)
        for p in participants:
            results.append({"user_id": p["user_id"], "share_value": None, "amount_owed": per_person})

    elif split_type == "exact":
        for p in participants:
            results.append({"user_id": p["user_id"], "share_value": None, "amount_owed": p["share_value"]})

    elif split_type == "percentage":
        for p in participants:
            amount = round(total * (p["share_value"] / 100), 2)
            results.append({"user_id": p["user_id"], "share_value": p["share_value"], "amount_owed": amount})

    elif split_type == "shares":
        total_shares = sum(p["share_value"] for p in participants)
        for p in participants:
            amount = round(total * (p["share_value"] / total_shares), 2)
            results.append({"user_id": p["user_id"], "share_value": p["share_value"], "amount_owed": amount})

    return results


def compute_direct_amount(total: float, split_type: str, share_value: float | None) -> float:
    if split_type == "equal":
        return round(total / 2, 2)
    elif split_type == "exact":
        return round(share_value, 2)
    elif split_type == "percentage":
        return round(total * (share_value / 100), 2)
    elif split_type == "shares":
        return round(total / 2, 2)
    return total
