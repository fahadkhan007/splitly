from fastapi import APIRouter

from app.core.dependencies import DB, CurrentUser

router = APIRouter()


@router.post("/chat")
async def chat(message: str, current_user: CurrentUser, db: DB):
    return {"reply": "AI integration coming soon", "user": current_user.full_name}
