from fastapi import APIRouter, HTTPException
from sqlalchemy import select, or_

from app.core.dependencies import DB, CurrentUser
from app.models.settlement import Settlement
from app.models.user import User
from app.schemas.settlement import SettlementCreate, SettlementResponse
from app.utils.balance import get_net_balance
from app.utils.email import send_settlement_notification

router = APIRouter()


@router.post("/", response_model=SettlementResponse, status_code=201)
async def create_settlement(body: SettlementCreate, current_user: CurrentUser, db: DB):
    net = await get_net_balance(current_user.id, body.payee_id, db)
    remaining = round(net - body.amount_paid, 2)

    settlement = Settlement(
        payer_id=current_user.id,
        payee_id=body.payee_id,
        amount_paid=body.amount_paid,
        remaining_amount=remaining,
        remark=body.remark,
        group_id=body.group_id,
    )
    db.add(settlement)
    await db.flush()

    payee = (await db.execute(select(User).where(User.id == body.payee_id))).scalar_one_or_none()
    if payee:
        send_settlement_notification(current_user.email, payee.email, body.amount_paid, current_user.full_name)

    return settlement


@router.get("/", response_model=list[SettlementResponse])
async def list_settlements(current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Settlement).where(
            or_(
                Settlement.payer_id == current_user.id,
                Settlement.payee_id == current_user.id,
            )
        )
    )
    return result.scalars().all()
