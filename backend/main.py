"""API FastAPI: sube una imagen, calcula el tamaño objetivo antes de
procesar, encola el trabajo, y sirve el resultado cuando termina.

Correr desde la raíz del proyecto con:
    uvicorn main:app --app-dir backend --reload --port 8000
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image

import db
import worker
from engine_bridge import SizingConfig, plan
from schemas import JobOut
from storage import UPLOADS_DIR, ensure_dirs
from validation import (
    UploadError,
    resolve_budget_px,
    validate_extension,
    validate_size,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_dirs()
    db.init_db()
    worker.start_worker()
    yield


app = FastAPI(title="Mejorador de Imágenes", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # uso local, no expuesto a internet
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/jobs", response_model=JobOut)
async def create_job(file: UploadFile = File(...), budget_mp: int = Form(2)) -> dict:
    try:
        ext = validate_extension(file.filename or "")
        content = await file.read()
        validate_size(content)
        budget_px = resolve_budget_px(budget_mp)
    except UploadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job_id = str(uuid.uuid4())
    input_path = UPLOADS_DIR / f"{job_id}{ext}"
    input_path.write_bytes(content)

    try:
        with Image.open(input_path) as image:
            width, height = image.size
    except Exception as exc:
        input_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400, detail=f"No se pudo leer la imagen: {exc}"
        ) from exc

    result = plan(width, height, SizingConfig(budget_px=budget_px))

    job = {
        "id": job_id,
        "original_filename": file.filename or input_path.name,
        "source_width": width,
        "source_height": height,
        "target_width": result.target.width,
        "target_height": result.target.height,
        "budget_px": budget_px,
        "passes": result.passes,
        "status": "queued",
        "stage": "en cola",
        "error_message": None,
        "input_path": str(input_path),
        "output_path": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db.insert_job(job)
    worker.enqueue(job_id)
    return job


@app.get("/api/jobs", response_model=list[JobOut])
def list_jobs_route() -> list[dict]:
    return db.list_jobs()


@app.get("/api/jobs/{job_id}", response_model=JobOut)
def get_job_route(job_id: str) -> dict:
    job = db.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return job


@app.get("/api/jobs/{job_id}/download")
def download_job(job_id: str) -> FileResponse:
    job = db.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    if job["status"] != "done" or not job["output_path"]:
        raise HTTPException(status_code=409, detail="El trabajo todavía no terminó")
    stem = Path(job["original_filename"]).stem
    return FileResponse(
        job["output_path"], filename=f"mejorada_{stem}.png", media_type="image/png"
    )


@app.delete("/api/jobs/{job_id}")
def delete_job_route(job_id: str) -> dict:
    job = db.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    Path(job["input_path"]).unlink(missing_ok=True)
    if job["output_path"]:
        Path(job["output_path"]).unlink(missing_ok=True)
    db.delete_job(job_id)
    return {"deleted": job_id}
