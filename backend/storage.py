"""Rutas de almacenamiento local: subidas, resultados y la base SQLite."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"
DB_PATH = DATA_DIR / "jobs.db"


def ensure_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
