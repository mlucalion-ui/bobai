"""SQLite engine + session helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

DB_PATH = Path(__file__).resolve().parents[1] / "var" / "bobai.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    # Import models so SQLModel.metadata sees them before create_all.
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _ensure_upload_columns()


def _ensure_upload_columns() -> None:
    """SQLite-only idempotent ALTER TABLE for columns added after Day 1."""
    with engine.begin() as conn:
        rows = conn.exec_driver_sql("PRAGMA table_info(upload)").all()
        cols = {r[1] for r in rows}
        if "text" not in cols:
            conn.exec_driver_sql("ALTER TABLE upload ADD COLUMN text TEXT")
        if "size_bytes" not in cols:
            conn.exec_driver_sql("ALTER TABLE upload ADD COLUMN size_bytes INTEGER")


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
