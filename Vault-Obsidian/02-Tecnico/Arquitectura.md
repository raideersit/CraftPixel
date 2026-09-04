---
tipo: tecnico
estado: decidido
actualizado: 2026-09-04
---

# Arquitectura

## Decisión: opción C — todo local en PC

Uso propio, no comercial. Sin necesidad de disponibilidad 24/7 ni de
multiusuario, la nube no aporta nada y sí agrega costo y complejidad.

Hardware disponible: GTX 1050, 2 GB VRAM, 16 GB RAM.

- Backend FastAPI corriendo en `localhost`. Sin túnel — no hace falta
  exponerlo fuera de la máquina.
- Motor: `realesrgan-ncnn-vulkan` (no la build PyTorch — 2 GB de VRAM no
  alcanza para el modelo completo cargado con margen de tiles grandes).
- Tiles obligatorios (`--tile 128` o `192`) para no agotar VRAM y para evitar
  costuras (ver [[Pipeline]]).
- Galería persistente → SQLite local, sin autenticación.

## Rutas descartadas

| Opción | Por qué se descarta |
|---|---|
| A) Navegador (ONNX Web + WebGPU) | Viable técnicamente en 2026, pero obliga a mantener dos rutas de inferencia con salida idéntica. Queda como optimización futura, no para el MVP |
| B) VPS con GPU propia | Costo fijo mensual ($58–110) sin sentido para uso personal esporádico |
| D) GPU serverless (Modal/RunPod) | Resolvía el caso de escala/multiusuario que no existe acá. Innecesario para uso propio |

## Restricción de licencias

No aplica — uso no comercial. `CodeFormer` (S-Lab License 1.0, no-comercial)
está permitido. Detalle → [[Modelos-IA]].

## Riesgo conocido

2 GB de VRAM es ajustado para restauración facial (GFPGAN/CodeFormer) además
del upscaler. Si no entra, fallback a CPU (lento, minutos, pero funciona).
Se valida al implementar, no bloquea el MVP.

## Enlaces

- Decisión formal → [[ADR-001-eleccion-stack]]
- Comparativa de modelos → [[Modelos-IA]]
- Flujo completo → [[Pipeline]]
