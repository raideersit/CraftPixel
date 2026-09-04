---
tipo: tecnico
estado: decidido
actualizado: 2026-09-04
---

# Modelos de super-resolución

Requisito: open source con licencia de uso comercial.

## Candidatos

| Modelo | Fuerte en | Licencia | Nota |
|---|---|---|---|
| Real-ESRGAN x4plus | fotografía general | BSD-3-Clause | línea base, build `ncnn-vulkan` por VRAM limitada (2 GB) |
| Real-ESRGAN anime6B | ilustración, arte digital | BSD-3-Clause | mejor para el caso de las capturas |
| SwinIR | detalle fino | Apache 2.0 | más lento |
| GFPGAN | restauración de rostros | Apache 2.0 | paso opcional |
| CodeFormer | restauración de rostros | S-Lab License 1.0 (no-comercial) | permitido — el proyecto es de uso propio, ver [[ADR-001-eleccion-stack]] |

Licencias verificadas. Sin restricción: uso propio, no comercial.

## Criterios de comparación

- Calidad visual al 100% de zoom
- Tiempo de inferencia para llevar 736x416 a 2 MP
- VRAM requerida
- Comportamiento en imágenes con texto y con rostros

## Observación

El paso de restauración facial es lo que más nota el usuario final, más que el
aumento de resolución en sí. Si el producto va a recibir fotos con personas,
esto no es opcional.

#### Decisión

Upscaler: Real-ESRGAN `ncnn-vulkan`, integrado y corriendo en el pipeline.
Restauración facial: GFPGAN, integrada y validada con imagen real (GPU,
fallback a CPU). CodeFormer queda como alternativa a evaluar más adelante.
