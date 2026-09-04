"""Validación de lo que sube el usuario, antes de tocar el motor ni el disco."""

from __future__ import annotations

from pathlib import Path

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
BUDGET_LEVELS_MP = {2: 2_000_000, 4: 4_000_000, 8: 8_000_000}


class UploadError(Exception):
    """Error de validación de un archivo subido."""


class FileTooLargeError(UploadError):
    """El archivo supera el límite de tamaño permitido."""


class UnsupportedUploadFormatError(UploadError):
    """Extensión de archivo no soportada."""


class InvalidBudgetLevelError(UploadError):
    """Nivel de salida (MP) no reconocido."""


def validate_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedUploadFormatError(
            f"Formato no soportado: {ext or '(sin extensión)'}. "
            f"Permitidos: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return ext


def validate_size(content: bytes) -> None:
    if len(content) > MAX_UPLOAD_BYTES:
        mb = len(content) / (1024 * 1024)
        raise FileTooLargeError(f"Archivo de {mb:.1f} MB supera el límite de 50 MB")


def resolve_budget_px(budget_mp: int) -> int:
    if budget_mp not in BUDGET_LEVELS_MP:
        raise InvalidBudgetLevelError(
            f"Nivel inválido: {budget_mp}. Válidos: {sorted(BUDGET_LEVELS_MP)}"
        )
    return BUDGET_LEVELS_MP[budget_mp]
