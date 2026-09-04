"""Cálculo de dimensiones de salida y plan de pasadas de inferencia.

Regla del producto (ver Vault-Obsidian/CLAUDE.md): la salida NO usa factor
fijo. Se calcula por presupuesto de megapíxeles manteniendo la relación de
aspecto, con un algoritmo asimétrico:

1. escala = sqrt(presupuesto / (ancho * alto))
2. el lado largo se trunca (floor)
3. el lado corto se deriva del lado largo con la relación de aspecto exacta
   y se redondea (round)

Truncar ambos lados falla en 749x468. Redondear ambos falla en 1200x703.
Solo esta combinación reproduce los tres casos medidos contra la referencia
real (LetsEnhance.io). No simplificar.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

DEFAULT_BUDGET_PX = 2_000_000
UPSCALE_FACTOR = 4


class DimensionError(Exception):
    """Dimensiones o presupuesto inválidos para calcular el tamaño de salida."""


@dataclass(frozen=True)
class SizingConfig:
    budget_px: int = DEFAULT_BUDGET_PX
    strict: bool = False  # si True, garantiza area <= budget_px


@dataclass(frozen=True)
class TargetSize:
    width: int
    height: int

    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass(frozen=True)
class UpscalePlan:
    source_width: int
    source_height: int
    target: TargetSize
    passes: int  # cantidad de pasadas de inferencia a 4x necesarias


def _target_from_long_side(
    long_side: int, *, width: int, height: int, long_is_width: bool
) -> TargetSize:
    if long_is_width:
        short_side = round(long_side * (height / width))
        return TargetSize(width=long_side, height=short_side)
    short_side = round(long_side * (width / height))
    return TargetSize(width=short_side, height=long_side)


def compute_target_size(
    width: int, height: int, config: SizingConfig = SizingConfig()
) -> TargetSize:
    """Calcula el tamaño de salida por presupuesto de megapíxeles."""
    if width <= 0 or height <= 0:
        raise DimensionError(f"Dimensiones inválidas: {width}x{height}")
    if config.budget_px <= 0:
        raise DimensionError(f"Presupuesto inválido: {config.budget_px}")

    long_is_width = width >= height
    source_long = width if long_is_width else height

    scale = math.sqrt(config.budget_px / (width * height))
    long_side_out = math.floor(source_long * scale)

    target = _target_from_long_side(
        long_side_out, width=width, height=height, long_is_width=long_is_width
    )

    if config.strict:
        while target.area > config.budget_px and long_side_out > 1:
            long_side_out -= 1
            target = _target_from_long_side(
                long_side_out, width=width, height=height, long_is_width=long_is_width
            )

    return target


def plan(width: int, height: int, config: SizingConfig = SizingConfig()) -> UpscalePlan:
    """Decide el tamaño de salida y cuántas pasadas de inferencia a 4x hacen falta."""
    target = compute_target_size(width, height, config)

    long_side_in = max(width, height)
    long_side_out = max(target.width, target.height)

    passes = 0
    current = long_side_in
    while current < long_side_out:
        current *= UPSCALE_FACTOR
        passes += 1
    passes = max(passes, 1)

    return UpscalePlan(
        source_width=width, source_height=height, target=target, passes=passes
    )


_REGRESSION_CASES = (
    ((736, 416), (1881, 1063)),
    ((1200, 703), (1847, 1082)),
    ((749, 468), (1789, 1118)),
)


def _run_regression_checks() -> bool:
    all_ok = True
    for (width, height), (expected_w, expected_h) in _REGRESSION_CASES:
        target = compute_target_size(width, height)
        ok = (target.width, target.height) == (expected_w, expected_h)
        status = "OK" if ok else "FALLA"
        print(
            f"{width}x{height} -> {target.width}x{target.height} "
            f"(esperado {expected_w}x{expected_h}) [{status}]"
        )
        all_ok = all_ok and ok
    return all_ok


if __name__ == "__main__":
    if not _run_regression_checks():
        sys.exit(1)
