"""Persistencia de trabajos en SQLite local. Sin autenticación (uso propio,
ver Vault-Obsidian/03-Decisiones/ADR-001-eleccion-stack.md)."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from storage import DB_PATH, ensure_dirs

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    original_filename TEXT NOT NULL,
    source_width INTEGER NOT NULL,
    source_height INTEGER NOT NULL,
    target_width INTEGER NOT NULL,
    target_height INTEGER NOT NULL,
    budget_px INTEGER NOT NULL,
    passes INTEGER NOT NULL,
    status TEXT NOT NULL,
    stage TEXT NOT NULL,
    error_message TEXT,
    input_path TEXT NOT NULL,
    output_path TEXT,
    created_at TEXT NOT NULL
);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(_SCHEMA)


def insert_job(job: dict[str, Any]) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, original_filename, source_width, source_height,
                target_width, target_height, budget_px, passes,
                status, stage, error_message, input_path, output_path, created_at
            ) VALUES (
                :id, :original_filename, :source_width, :source_height,
                :target_width, :target_height, :budget_px, :passes,
                :status, :stage, :error_message, :input_path, :output_path, :created_at
            )
            """,
            job,
        )


def update_job(job_id: str, **fields: Any) -> None:
    if not fields:
        return
    columns = ", ".join(f"{key} = :{key}" for key in fields)
    fields["id"] = job_id
    with get_connection() as conn:
        conn.execute(f"UPDATE jobs SET {columns} WHERE id = :id", fields)


def get_job(job_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None


def list_jobs() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]


def delete_job(job_id: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
