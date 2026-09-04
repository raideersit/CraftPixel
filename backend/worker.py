"""Worker en background: procesa trabajos de la cola secuencialmente.

Un solo worker porque hay una sola GPU (GTX 1050) — no tiene sentido
paralelizar inferencia sobre el mismo dispositivo.
"""

from __future__ import annotations

import queue
import threading
from pathlib import Path

import db
from engine_bridge import (
    DimensionError,
    FaceRestoreError,
    InferenceError,
    ResizeError,
    TargetSize,
    default_face_restore_config,
    default_inference_config,
    resize_to_target,
    restore_faces,
    upscale_4x,
)
from storage import OUTPUTS_DIR

_job_queue: queue.Queue[str] = queue.Queue()
_inference_config = default_inference_config()
_face_restore_config = default_face_restore_config()


def enqueue(job_id: str) -> None:
    _job_queue.put(job_id)


def start_worker() -> None:
    thread = threading.Thread(target=_worker_loop, daemon=True)
    thread.start()


def _worker_loop() -> None:
    while True:
        job_id = _job_queue.get()
        try:
            _process_job(job_id)
        finally:
            _job_queue.task_done()


def _process_job(job_id: str) -> None:
    job = db.get_job(job_id)
    if job is None:
        return

    input_path = Path(job["input_path"])
    passes = job["passes"]
    tmp_dir = OUTPUTS_DIR / f".tmp_{job_id}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        db.update_job(
            job_id, status="processing", stage=f"inferencia (pasada 1/{passes})"
        )

        current_input = input_path
        for i in range(passes):
            is_last = i == passes - 1
            current_output = (
                tmp_dir / "4x_final.png" if is_last else tmp_dir / f"pass_{i}.png"
            )
            upscale_4x(current_input, current_output, _inference_config)
            current_input = current_output
            if not is_last:
                db.update_job(job_id, stage=f"inferencia (pasada {i + 2}/{passes})")

        db.update_job(job_id, stage="restaurando rostros")
        face_output = tmp_dir / "face_restored.png"
        restore_faces(current_input, face_output, _face_restore_config)
        current_input = face_output

        db.update_job(job_id, stage="redimensionando")
        target = TargetSize(width=job["target_width"], height=job["target_height"])
        output_path = OUTPUTS_DIR / f"{job_id}.png"
        resize_to_target(current_input, output_path, target)

        db.update_job(
            job_id, status="done", stage="listo", output_path=str(output_path)
        )
    except (InferenceError, ResizeError, DimensionError, FaceRestoreError) as exc:
        db.update_job(job_id, status="error", stage="error", error_message=str(exc))
    except Exception as exc:  # último límite: no debe morir el hilo del worker
        db.update_job(
            job_id,
            status="error",
            stage="error",
            error_message=f"Error inesperado: {exc}",
        )
    finally:
        for leftover in tmp_dir.glob("*"):
            leftover.unlink(missing_ok=True)
        tmp_dir.rmdir()
