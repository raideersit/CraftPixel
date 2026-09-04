"""Restauración de rostros con GFPGAN. Corre después del upscaler y antes del
resize final (ver Vault-Obsidian/02-Tecnico/Pipeline.md).

A diferencia del upscaler (ncnn-vulkan, sin PyTorch por límite de VRAM),
GFPGAN sí necesita PyTorch. El modelo es chico (~333 MB) y corre después de
que el upscaler ya liberó su propia memoria, así que suele entrar en GPU.
Si no entra, cae a CPU (lento, pero funciona).

Requiere el archivo de pesos GFPGANv1.4.pth (no viene empaquetado):
https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cv2

DeviceName = Literal["cuda", "cpu"]


class FaceRestoreError(Exception):
    """Error base de la restauración facial."""


class WeightsNotFoundError(FaceRestoreError):
    """No se encontraron los pesos de GFPGAN."""


class VRAMExhaustedError(FaceRestoreError):
    """La GPU se quedó sin memoria durante la restauración facial."""


@dataclass(frozen=True)
class FaceRestoreConfig:
    weights_path: Path = Path("engine/models_face/GFPGANv1.4.pth")
    upscale: int = 1  # la imagen ya viene escalada por el upscaler; no duplicar
    device: DeviceName = "cuda"


_restorer_cache: dict[DeviceName, object] = {}


def _build_restorer(config: FaceRestoreConfig, device: DeviceName):
    if not config.weights_path.exists():
        raise WeightsNotFoundError(
            f"No se encontró {config.weights_path}. Descargalo de "
            "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth"
        )

    import torch
    from gfpgan import GFPGANer

    return GFPGANer(
        model_path=str(config.weights_path),
        upscale=config.upscale,
        arch="clean",
        channel_multiplier=2,
        bg_upsampler=None,
        device=torch.device(device),
    )


def _get_restorer(config: FaceRestoreConfig, device: DeviceName):
    """Instancia GFPGANer una sola vez por dispositivo (cargar pesos es lento)."""
    cached = _restorer_cache.get(device)
    if cached is not None:
        return cached
    restorer = _build_restorer(config, device)
    _restorer_cache[device] = restorer
    return restorer


def restore_faces(
    input_path: Path,
    output_path: Path,
    config: FaceRestoreConfig = FaceRestoreConfig(),
) -> bool:
    """Restaura rostros en input_path, escribe en output_path.

    Devuelve True si detectó al menos un rostro y lo restauró, False si no
    encontró ninguno (en ese caso escribe la imagen sin modificar).
    """
    if not input_path.exists():
        raise FaceRestoreError(f"No existe el archivo de entrada: {input_path}")

    img = cv2.imread(str(input_path))
    if img is None:
        raise FaceRestoreError(f"No se pudo leer la imagen: {input_path}")

    device = config.device
    try:
        restorer = _get_restorer(config, device)
        cropped_faces, _, restored_img = restorer.enhance(
            img, has_aligned=False, only_center_face=False, paste_back=True
        )
    except RuntimeError as exc:
        if device == "cpu" or "out of memory" not in str(exc).lower():
            raise VRAMExhaustedError(
                f"Fallo de memoria en restauración facial: {exc}"
            ) from exc
        import torch

        torch.cuda.empty_cache()
        restorer = _get_restorer(config, "cpu")
        cropped_faces, _, restored_img = restorer.enhance(
            img, has_aligned=False, only_center_face=False, paste_back=True
        )

    # con paste_back=True, GFPGANer siempre devuelve una imagen (nunca None),
    # incluso sin rostros detectados: en ese caso es la entrada sin modificar.
    # La señal real de "encontró algo" es cropped_faces, no restored_img.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), restored_img)
    return len(cropped_faces) > 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python engine/face_restore.py <entrada> <salida>")
        sys.exit(1)

    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        found = restore_faces(src, dst)
        etiqueta = "rostro restaurado" if found else "sin rostros detectados"
        print(f"OK ({etiqueta}): {dst}")
    except FaceRestoreError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
