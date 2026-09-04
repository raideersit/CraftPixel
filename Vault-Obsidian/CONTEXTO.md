---
tipo: contexto
actualizado: 2026-09-04
---

# CONTEXTO

> Este es el único archivo que pego al abrir un chat nuevo.
> Máximo 40 líneas. Si crece más, algo debe moverse a una nota propia.

## Qué construyo

App web de super-resolución con IA. El usuario sube una imagen y recibe una
versión ampliada y nítida. Referencia de producto: LetsEnhance.io.

## Regla de dimensionado (lo que define el producto)

La salida NO usa factor fijo. Se calcula por presupuesto de megapíxeles
manteniendo la relación de aspecto. Nivel base = 2 MP.

| Entrada | Salida | Factor |
|---|---|---|
| 736x416 | 1881x1063 | 2.55x |
| 1200x703 | 1847x1082 | 1.54x |
| 749x468 | 1789x1118 | 2.39x |

## Estado actual

- Fase: implementación del pipeline. `ADR-001` cerrado, stack decidido.
- Funciona de punta a punta, incluida restauración facial (GFPGAN):
  subida → cola → Real-ESRGAN → GFPGAN → resize → galería.
- Bloqueante: ninguno.
- Próximo paso: revisar la pestaña Galería contra jobs reales.

## Stack

- Decidido (`ADR-001`): todo local en PC, sin túnel ni servidor expuesto.
- Motor: Real-ESRGAN `ncnn-vulkan` (GTX 1050, 2 GB VRAM), tiles obligatorios.
- Falta integrar: restauración facial (GFPGAN/CodeFormer).

## Dónde está todo

- Visión y alcance → [[Vision]]
- Cómo se comporta la referencia → [[Referencia-LetsEnhance]]
- Arquitectura → [[Arquitectura]]
- Decisiones cerradas → carpeta `03-Decisiones`
- Qué hice cada día → carpeta `04-Bitacora`
