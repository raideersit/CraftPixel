"""Puente al motor en engine/ (no es un paquete Python instalable, es un
directorio de scripts hermano de backend/). Centraliza el sys.path hack acá
para no repetirlo en cada módulo del backend.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from sizing import (  # noqa: E402
    DimensionError,
    SizingConfig,
    TargetSize,
    UpscalePlan,
    plan,
)
from inference import (  # noqa: E402
    ExecutableNotFoundError,
    InferenceConfig,
    InferenceError,
    InferenceTimeoutError,
    VRAMExhaustedError,
    upscale_4x,
)
from resize import (  # noqa: E402
    ResizeConfig,
    ResizeError,
    UnsupportedFormatError,
    resize_to_target,
)
from face_restore import (  # noqa: E402
    FaceRestoreConfig,
    FaceRestoreError,
    VRAMExhaustedError as FaceVRAMExhaustedError,
    WeightsNotFoundError as FaceWeightsNotFoundError,
    restore_faces,
)


def default_inference_config() -> InferenceConfig:
    """InferenceConfig con rutas absolutas a engine/, sin importar el cwd."""
    return InferenceConfig(
        executable=_ENGINE_DIR / "realesrgan-ncnn-vulkan.exe",
        model_dir=_ENGINE_DIR / "models",
    )


def default_face_restore_config() -> FaceRestoreConfig:
    """FaceRestoreConfig con ruta absoluta a los pesos de GFPGAN, sin importar el cwd."""
    return FaceRestoreConfig(weights_path=_ENGINE_DIR / "models_face" / "GFPGANv1.4.pth")
