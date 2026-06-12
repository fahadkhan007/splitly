from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.core.config import settings
from app.routers import auth, users, friends, groups, expenses, settlements, chat, ai

app = FastAPI(
    title="Splitly API",
    description="Expense splitting app",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(friends.router, prefix="/api/v1/friends", tags=["Friends"])
app.include_router(groups.router, prefix="/api/v1/groups", tags=["Groups"])
app.include_router(expenses.router, prefix="/api/v1/expenses", tags=["Expenses"])
app.include_router(settlements.router, prefix="/api/v1/settlements", tags=["Settlements"])
app.include_router(chat.router, prefix="/ws", tags=["Chat"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])


@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(openapi_url="/openapi.json", title="Splitly API")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
