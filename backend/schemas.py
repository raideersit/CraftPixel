"""Modelos de request/response de la API."""

from __future__ import annotations

from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    original_filename: str
    source_width: int
    source_height: int
    target_width: int
    target_height: int
    budget_px: int
    passes: int
    status: str
    stage: str
    error_message: str | None
    input_path: str
    output_path: str | None
    created_at: str
