"""Wrapper del motor de inferencia: realesrgan-ncnn-vulkan.

No se usa la build PyTorch de Real-ESRGAN: la GPU disponible (GTX 1050,
2 GB VRAM) no tiene margen para cargarla con tiles grandes. ncnn-vulkan es
liviano y corre bien en GPUs chicas. Decisión completa en
Vault-Obsidian/03-Decisiones/ADR-001-eleccion-stack.md.

Requiere el binario `realesrgan-ncnn-vulkan` (no viene empaquetado):
https://github.com/xinntao/Real-ESRGAN/releases
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ModelName = Literal["realesrgan-x4plus", "realesrgan-x4plus-anime"]

DEFAULT_TILE_SIZE = 192
DEFAULT_TIMEOUT_S = 300

_VRAM_ERROR_MARKERS = (
    "out of memory",
    "vkallocatememory",
    "vkqueuesubmit failed",
    "cudamalloc",
)


class InferenceError(Exception):
    """Error base del motor de inferencia."""


class ExecutableNotFoundError(InferenceError):
    """No se encontró el binario realesrgan-ncnn-vulkan."""


class VRAMExhaustedError(InferenceError):
    """La GPU se quedó sin memoria durante la inferencia."""


class InferenceTimeoutError(InferenceError):
    """La inferencia superó el tiempo límite configurado."""


@dataclass(frozen=True)
class InferenceConfig:
    executable: Path = Path("engine/realesrgan-ncnn-vulkan.exe")
    model_dir: Path = Path("engine/models")
    model: ModelName = "realesrgan-x4plus"
    tile_size: int = DEFAULT_TILE_SIZE
    gpu_id: int = 0
    timeout_s: int = DEFAULT_TIMEOUT_S


def upscale_4x(
    input_path: Path, output_path: Path, config: InferenceConfig = InferenceConfig()
) -> None:
    """Corre una pasada de inferencia a 4x sobre input_path, escribe en output_path."""
    if not config.executable.exists():
        raise ExecutableNotFoundError(
            f"No se encontró el binario en {config.executable}. Descargalo de "
            "https://github.com/xinntao/Real-ESRGAN/releases y colocalo ahí, "
            "o ajustá InferenceConfig.executable."
        )
    if not input_path.exists():
        raise InferenceError(f"No existe el archivo de entrada: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        str(config.executable),
        "-i", str(input_path),
        "-o", str(output_path),
        "-m", str(config.model_dir),
        "-n", config.model,
        "-t", str(config.tile_size),
        "-g", str(config.gpu_id),
        "-s", "4",
    ]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=config.timeout_s
        )
    except subprocess.TimeoutExpired as exc:
        raise InferenceTimeoutError(
            f"Inferencia de {input_path.name} superó {config.timeout_s}s"
        ) from exc

    if result.returncode != 0:
        stderr_lower = result.stderr.lower()
        if any(marker in stderr_lower for marker in _VRAM_ERROR_MARKERS):
            raise VRAMExhaustedError(
                f"GPU sin memoria procesando {input_path.name}. "
                f"Bajá InferenceConfig.tile_size (actual: {config.tile_size})."
            )
        raise InferenceError(
            f"realesrgan-ncnn-vulkan falló (código {result.returncode}): "
            f"{result.stderr.strip()}"
        )


def run_passes(
    input_path: Path,
    output_path: Path,
    passes: int,
    config: InferenceConfig = InferenceConfig(),
    *,
    tmp_dir: Path | None = None,
) -> None:
    """Encadena `passes` pasadas de 4x. `passes` viene de engine.sizing.plan()."""
    if passes < 1:
        raise InferenceError(f"passes debe ser >= 1, recibido: {passes}")

    tmp_dir = tmp_dir or output_path.parent / ".inference_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    current_input = input_path
    try:
        for i in range(passes):
            is_last = i == passes - 1
            current_output = output_path if is_last else tmp_dir / f"pass_{i}.png"
            upscale_4x(current_input, current_output, config)
            current_input = current_output
    finally:
        for leftover in tmp_dir.glob("pass_*.png"):
            leftover.unlink(missing_ok=True)
        if tmp_dir.exists() and not any(tmp_dir.iterdir()):
            tmp_dir.rmdir()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python engine/inference.py <entrada> <salida>")
        sys.exit(1)

    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        upscale_4x(src, dst)
        print(f"OK: {dst}")
    except InferenceError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
