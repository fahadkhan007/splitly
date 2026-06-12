from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import DB
from app.core.security import hash_password, verify_password, create_access_token, create_email_token, decode_token
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.utils.email import send_verification_email
from app.core.config import settings

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DB):
    existing = (await db.execute(select(User).where(User.email == body.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    token = create_email_token(body.email)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    send_verification_email(body.email, verify_url)

    return {"message": "Account created. Check your email to verify."}


@router.get("/verify-email")
async def verify_email(token: str, db: DB):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email or payload.get("type") != "email":
            raise ValueError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    return {"message": "Email verified. You can now log in."}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DB):
    user = (await db.execute(select(User).where(User.email == body.email))).scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/resend-verification")
async def resend_verification(email: str, db: DB):
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Already verified"}

    token = create_email_token(email)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    send_verification_email(email, verify_url)
    return {"message": "Verification email resent"}
