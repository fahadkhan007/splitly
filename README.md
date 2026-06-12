# Splitly — Expense Splitting App

A full-stack expense splitting application built as a job assignment. Splitly lets users split bills equally, by exact amounts, by percentage, or by shares — with real-time updates and in-expense chat powered by WebSockets.

---

## Live Demo

| Service | URL |
|---|---|
| Frontend | _(Vercel URL — add after deploy)_ |
| Backend API | _(Railway URL — add after deploy)_ |
| API Docs | `<backend-url>/docs` |

---

## Features

- **Email Authentication** — Register, verify email, login with JWT
- **Friend System** — Invite friends by email, accept requests
- **Group Management** — Create groups, add/remove members
- **Expense Splitting** — 4 split types: Equal, Exact amounts, Percentage, Shares
- **Balance Tracking** — Live net balance per friend and per group
- **Settle Up** — Record full or partial payments
- **Real-Time Updates** — Expenses appear instantly via WebSockets
- **In-Expense Chat** — Participants can chat on each expense in real-time
- **AI Chatbot** — Ask questions about your expenses in plain English
- **Email Notifications** — On expense creation, settlement, and friend invites

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite |
| Backend | FastAPI (Python 3.13) |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Real-Time | FastAPI WebSockets |
| Auth | JWT (python-jose) |
| Password | bcrypt (passlib) |
| Email | Resend |
| AI | LangChain / LangGraph |
| Package Manager (Python) | uv |
| Package Manager (JS) | npm |
| Backend Hosting | Railway |
| Frontend Hosting | Vercel |

---

## Project Structure

```
splitly/
├── AI_CONTEXT.md          ← Full product + engineering context
├── BUILD_PLAN.md          ← Build plan with AI collaboration notes
├── KEY_PROMPTS.txt        ← Key prompts used during development
├── README.md
│
├── backend/
│   ├── .env.example       ← Environment variable template
│   ├── pyproject.toml     ← Python dependencies (uv)
│   ├── main.py            ← Uvicorn entry point
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/      ← Database migrations
│   └── app/
│       ├── main.py        ← FastAPI app + router wiring
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── security.py
│       │   └── dependencies.py
│       ├── models/        ← SQLAlchemy ORM models (9 tables)
│       ├── schemas/       ← Pydantic request/response schemas
│       ├── routers/       ← API endpoints
│       └── utils/
│           ├── balance.py ← Balance calculation logic
│           └── email.py   ← Email sending via Resend
│
└── frontend/
    ├── package.json
    └── src/
        ├── api/           ← Axios API clients per resource
        ├── context/       ← AuthContext (JWT + user state)
        ├── hooks/         ← useAuth, useWebSocket
        ├── pages/         ← One file per screen
        └── types/         ← TypeScript interfaces
```

---

## Database Schema

The app uses 9 tables:

| Table | Purpose |
|---|---|
| `users` | User accounts |
| `friendships` | Friend requests and accepted connections |
| `groups` | Expense groups |
| `group_members` | Group membership (many-to-many) |
| `group_expenses` | Group-level expenses |
| `group_expense_participants` | Who owes what per group expense |
| `direct_expenses` | 1-on-1 expenses between two users |
| `settlements` | Payment records |
| `expense_messages` | In-expense real-time chat |

---

## Setup — Backend

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) installed
- PostgreSQL running locally or on Railway

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/splitly.git
cd splitly/backend
```

### 2. Create `.env` file

```bash
cp .env.example .env
```

Fill in the values (see Environment Variables section below).

### 3. Install dependencies

```bash
uv sync
```

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the development server

```bash
uv run uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`
Docs (Scalar UI) at `http://localhost:8000/docs`

---

## Setup — Frontend

### Prerequisites

- Node.js 18+
- npm

### 1. Navigate to frontend

```bash
cd splitly/frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Create `.env` file

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### 4. Start development server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## Environment Variables

Create `backend/.env` with the following:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/splitly
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/splitly

# JWT
SECRET_KEY=your-secret-key-here-make-it-long-and-random

# Email (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=Splitly <noreply@yourdomain.com>

# Frontend URL (used in email links)
FRONTEND_URL=http://localhost:5173
```

### Getting these values

| Variable | Where to get it |
|---|---|
| `DATABASE_URL` | Your local PostgreSQL or Railway DB connection string |
| `SECRET_KEY` | Run `python -c "import secrets; print(secrets.token_hex(32))"` |
| `RESEND_API_KEY` | [resend.com](https://resend.com) → API Keys |
| `EMAIL_FROM` | A verified sender domain on Resend |

---

## API Endpoints

All endpoints prefixed with `/api/v1/`

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/verify-email?token=` | Verify email address |
| POST | `/auth/resend-verification` | Resend verification email |

### Users
| Method | Path | Description |
|---|---|---|
| GET | `/users/me` | Get my profile |
| PUT | `/users/me` | Update my profile |
| GET | `/users/me/balances` | Net balance with all friends |

### Friends
| Method | Path | Description |
|---|---|---|
| GET | `/friends/` | List accepted friends |
| POST | `/friends/invite` | Invite friend by email |
| GET | `/friends/pending` | Incoming friend requests |
| POST | `/friends/{id}/accept` | Accept a friend request |
| GET | `/friends/{id}/balance` | Net balance with a friend |

### Groups
| Method | Path | Description |
|---|---|---|
| GET | `/groups/` | List my groups |
| POST | `/groups/` | Create a group |
| GET | `/groups/{id}` | Group detail + members |
| POST | `/groups/{id}/members` | Add a member |
| DELETE | `/groups/{id}/members/{userId}` | Remove a member |

### Expenses
| Method | Path | Description |
|---|---|---|
| POST | `/expenses/group` | Create group expense |
| PUT | `/expenses/group/{id}` | Edit group expense (creator only) |
| DELETE | `/expenses/group/{id}` | Delete group expense (creator only) |
| POST | `/expenses/direct` | Create 1-on-1 expense |
| PUT | `/expenses/direct/{id}` | Edit direct expense (creator only) |
| DELETE | `/expenses/direct/{id}` | Delete direct expense (creator only) |

### Settlements
| Method | Path | Description |
|---|---|---|
| POST | `/settlements/` | Record a payment |
| GET | `/settlements/` | List my settlements |

### AI
| Method | Path | Description |
|---|---|---|
| POST | `/ai/chat` | Ask AI about your expenses |

### WebSocket
| Path | Description |
|---|---|
| `ws://host/ws/expense/{type}/{id}?token=<jwt>` | Real-time chat on an expense |

---

## Split Type Logic

When creating an expense, choose a split type:

| Type | How it works |
|---|---|
| `equal` | Total ÷ number of participants |
| `exact` | You enter each person's exact amount |
| `percentage` | Each person gets a % (must sum to 100) |
| `shares` | Each person gets N shares; proportion calculated automatically |

---

## Authentication

All protected endpoints require a JWT in the Authorization header:

```
Authorization: Bearer <your_token>
```

Get the token from `POST /api/v1/auth/login`.

---

## Deployment

### Backend (Railway)

1. Push code to GitHub
2. Create a new Railway project → Deploy from GitHub repo
3. Add a PostgreSQL database in Railway
4. Set all environment variables in Railway dashboard
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Run migrations: `uv run alembic upgrade head` (Railway shell)

### Frontend (Vercel)

1. Import the repo in Vercel
2. Set root directory to `frontend`
3. Set environment variables:
   - `VITE_API_URL` = your Railway backend URL
   - `VITE_WS_URL` = `wss://` version of your Railway backend URL
4. Deploy

---

## AI Tool Used

**Antigravity** (Google DeepMind)

The AI was used as a junior engineering collaborator throughout the project. It was instructed not to assume requirements, to ask detailed questions about product scope and engineering decisions, and to maintain `AI_CONTEXT.md` as a living source of truth.

See `AI_CONTEXT.md` for the full product + engineering context, and `KEY_PROMPTS.txt` for key prompts used.

---

## Local Testing (Quick Start)

After starting the server:

1. Go to `http://localhost:8000/docs`
2. Register: `POST /api/v1/auth/register`
3. Manually verify your email in pgAdmin: `UPDATE users SET is_verified = true WHERE email = 'your@email.com';`
4. Login: `POST /api/v1/auth/login` — copy the token
5. Click the lock icon 🔒 in Scalar docs and paste `Bearer <token>`
6. Test any endpoint

---

## Contributing

This is an assignment project and not open for contribution. Feel free to fork and build on it.

---

## License

MIT
