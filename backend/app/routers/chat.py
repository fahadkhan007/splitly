from uuid import UUID
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.models.chat import ExpenseMessage, ExpenseType
from app.models.expense import GroupExpense, GroupExpenseParticipant, DirectExpense
from app.models.user import User
from app.schemas.chat import MessageResponse

router = APIRouter()

active_connections: Dict[str, List[WebSocket]] = {}


async def get_user_from_token(token: str, db: AsyncSession):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
    except Exception:
        return None
    return (await db.execute(select(User).where(User.id == UUID(user_id)))).scalar_one_or_none()


async def is_expense_participant(expense_id: UUID, expense_type: str, user_id: UUID, db: AsyncSession) -> bool:
    if expense_type == "group":
        row = (await db.execute(
            select(GroupExpenseParticipant).where(
                GroupExpenseParticipant.expense_id == expense_id,
                GroupExpenseParticipant.user_id == user_id
            )
        )).scalar_one_or_none()
        return row is not None
    else:
        expense = (await db.execute(
            select(DirectExpense).where(DirectExpense.id == expense_id)
        )).scalar_one_or_none()
        if not expense:
            return False
        return user_id in [expense.paid_by, expense.owed_by]


def get_channel_key(expense_id: UUID, expense_type: str) -> str:
    return f"{expense_type}:{expense_id}"


@router.websocket("/expense/{expense_type}/{expense_id}")
async def expense_chat(websocket: WebSocket, expense_id: UUID, expense_type: str, token: str = Query(...)):
    async with AsyncSessionLocal() as db:
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=4001)
            return

        allowed = await is_expense_participant(expense_id, expense_type, user.id, db)
        if not allowed:
            await websocket.close(code=4003)
            return

        await websocket.accept()

        channel = get_channel_key(expense_id, expense_type)
        if channel not in active_connections:
            active_connections[channel] = []
        active_connections[channel].append(websocket)

        try:
            while True:
                text = await websocket.receive_text()

                msg = ExpenseMessage(
                    expense_id=expense_id,
                    expense_type=ExpenseType(expense_type),
                    sender_id=user.id,
                    message=text,
                )
                db.add(msg)
                await db.commit()
                await db.refresh(msg)

                payload = {
                    "id": str(msg.id),
                    "expense_id": str(expense_id),
                    "expense_type": expense_type,
                    "sender_id": str(user.id),
                    "sender_name": user.full_name,
                    "message": text,
                    "created_at": msg.created_at.isoformat(),
                }

                for conn in active_connections.get(channel, []):
                    await conn.send_json(payload)

        except WebSocketDisconnect:
            active_connections[channel].remove(websocket)


@router.get("/expense/{expense_type}/{expense_id}/history", response_model=list[MessageResponse])
async def get_chat_history(expense_id: UUID, expense_type: str, current_user=None, db: AsyncSession = None):
    messages = (await db.execute(
        select(ExpenseMessage).where(
            ExpenseMessage.expense_id == expense_id,
            ExpenseMessage.expense_type == ExpenseType(expense_type),
        ).order_by(ExpenseMessage.created_at)
    )).scalars().all()

    result = []
    for msg in messages:
        sender = (await db.execute(select(User).where(User.id == msg.sender_id))).scalar_one_or_none()
        result.append(MessageResponse(
            id=msg.id,
            expense_id=msg.expense_id,
            expense_type=msg.expense_type.value,
            sender_id=msg.sender_id,
            sender_name=sender.full_name if sender else "Unknown",
            message=msg.message,
            created_at=msg.created_at,
        ))
    return result
