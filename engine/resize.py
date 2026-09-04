"""Redimensionado final al tamaño exacto calculado por engine.sizing.

Pipeline: inferencia a 4x (una o más pasadas) -> Lanczos al tamaño exacto.
Bajar con Lanczos da mejor resultado que subir, por eso sizing.plan()
siempre sobre-infiere y este paso reduce. Ver Vault-Obsidian/02-Tecnico/Pipeline.md.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from sizing import TargetSize  # noqa: E402

OutputFormat = Literal["png", "jpg", "webp"]

DEFAULT_JPEG_QUALITY = 92

_SUPPORTED_INPUT_FORMATS = {"JPEG", "PNG", "WEBP"}


class ResizeError(Exception):
    """Error al redimensionar la imagen al tamaño objetivo."""


class UnsupportedFormatError(ResizeError):
    """Formato de imagen no soportado."""


@dataclass(frozen=True)
class ResizeConfig:
    output_format: OutputFormat = "png"
    jpeg_quality: int = DEFAULT_JPEG_QUALITY


def resize_to_target(
    input_path: Path,
    output_path: Path,
    target: TargetSize,
    config: ResizeConfig = ResizeConfig(),
) -> None:
    """Redimensiona input_path al tamaño exacto de target con Lanczos."""
    if not input_path.exists():
        raise ResizeError(f"No existe el archivo de entrada: {input_path}")

    try:
        image = Image.open(input_path)
        image.load()
    except Exception as exc:
        raise ResizeError(f"No se pudo abrir {input_path}: {exc}") from exc

    if image.format not in _SUPPORTED_INPUT_FORMATS:
        raise UnsupportedFormatError(
            f"Formato no soportado: {image.format} ({input_path})"
        )

    resized = image.convert("RGB").resize(
        (target.width, target.height), Image.Resampling.LANCZOS
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if config.output_format == "jpg":
        pillow_format, save_kwargs = "JPEG", {
            "quality": config.jpeg_quality,
            "optimize": True,
        }
    elif config.output_format == "webp":
        pillow_format, save_kwargs = "WEBP", {"quality": config.jpeg_quality}
    else:
        pillow_format, save_kwargs = "PNG", {}

    try:
        resized.save(output_path, format=pillow_format, **save_kwargs)
    except OSError as exc:
        raise ResizeError(f"No se pudo guardar {output_path}: {exc}") from exc


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python engine/resize.py <entrada> <salida> <ancho> <alto>")
        sys.exit(1)

    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    target = TargetSize(width=int(sys.argv[3]), height=int(sys.argv[4]))
    try:
        resize_to_target(src, dst, target)
        print(f"OK: {dst} -> {target.width}x{target.height}")
    except ResizeError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
