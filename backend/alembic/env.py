from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# ── Alembic config ────────────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Load app settings + all models ───────────────────────────────────────────
from app.core.config import settings
from app.core.database import Base
import app.models  # noqa: F401 — registers all models with Base

target_metadata = Base.metadata


# ── Offline migrations ────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Run migrations without a live DB connection."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online migrations ─────────────────────────────────────────────────────────
def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    # Create engine directly from settings — avoids configparser % interpolation issues
    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
