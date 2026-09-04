---
tipo: adr
numero: 001
estado: aceptada
fecha: 2026-09-04
---

# ADR-001: Elección de arquitectura y stack

## Contexto

Había tres rutas evaluadas para el motor de inferencia (navegador, VPS con
GPU, PC local + túnel), más una cuarta sumada durante la evaluación (GPU
serverless). El criterio "costo mensual con 500 imágenes" asumía uso con
volumen y disponibilidad constante.

Se aclaró que el proyecto es de **uso propio, no comercial, sin necesidad de
disponibilidad 24/7**. Eso invalida el criterio de escala y cambia la
decisión por completo.

## Opciones consideradas

| Opción | Costo/mes | Disponibilidad | Dificultad |
|---|---|---|---|
| A) Navegador (WebGPU) | $0 | Depende del hardware del visitante | Alta |
| B) VPS con GPU dedicada | $58–110 fijo | 24/7 | Media |
| C) PC local, sin túnel | $0 | Solo cuando el PC está prendido | Baja |
| D) GPU serverless (Modal) | ~$0–2 (créditos gratis cubren el uso) | Bajo demanda | Media |

Con 500 img/mes hipotéticas, D ganaba por escalar a cero. Con uso propio
esporádico, esa ventaja no aplica: no hay usuarios externos que necesiten
disponibilidad constante.

## Decisión

**Opción C: todo local en PC**, sin servidor expuesto ni túnel.

- Motor: `realesrgan-ncnn-vulkan` (no PyTorch — la GPU disponible, una
  GTX 1050 con 2 GB de VRAM, no tiene margen para la build completa).
- Tiles obligatorios por límite de VRAM.
- Restauración facial: GFPGAN o CodeFormer, con fallback a CPU si no entra
  en memoria.
- Se levanta la restricción de licencia comercial: al ser uso propio,
  CodeFormer (no-comercial) queda habilitado.

## Consecuencias

- Costo de infraestructura: $0 permanente.
- Disponibilidad atada a que la PC esté encendida — aceptable para uso
  propio, sería inaceptable si el proyecto pasara a tener otros usuarios.
- Sin necesidad de auth ni multiusuario: galería en SQLite local.
- Si el alcance cambia a uso compartido o comercial en el futuro, este ADR
  debe revisarse — la opción D (serverless) es la que reemplazaría a C, no
  B, por relación costo/uso.
- El worker se construye igual como contenedor portable (regla de
  `CLAUDE.md`), así que migrar a D más adelante no implica reescribir el
  motor, solo el despliegue.

## Estado

aceptada
