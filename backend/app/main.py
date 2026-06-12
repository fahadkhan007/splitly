from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.core.config import settings

app = FastAPI(
    title="Splitly API",
    description="Expense splitting app — track, split, and settle shared expenses.",
    version="1.0.0",
    docs_url=None,    # disable default Swagger UI
    redoc_url=None,   # disable default ReDoc
    openapi_url="/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Scalar API Docs ───────────────────────────────────────────────────────────
@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title="Splitly API",
    )

# ── Routers (uncommented as each router is built) ─────────────────────────────
# from app.routers import auth, users, friends, groups, expenses, settlements, ai
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(friends.router, prefix="/api/v1/friends", tags=["Friends"])
# app.include_router(groups.router, prefix="/api/v1/groups", tags=["Groups"])
# app.include_router(expenses.router, prefix="/api/v1/expenses", tags=["Expenses"])
# app.include_router(settlements.router, prefix="/api/v1/settlements", tags=["Settlements"])
# app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
