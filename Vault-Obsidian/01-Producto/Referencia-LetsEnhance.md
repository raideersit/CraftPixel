---
tipo: producto
estado: medido
actualizado: 2026-09-04
---

# Referencia: LetsEnhance.io

Producto que tomo como modelo de UX y comportamiento.

## Hallazgo principal

No escala por factor fijo. Escala hasta llenar un **presupuesto de megapíxeles**
respetando la relación de aspecto original. Medido sobre resultados reales:

| Entrada | Salida | Píxeles salida | Factor |
|---|---|---|---|
| 736x416 | 1881x1063 | 1.999.503 | 2.55x |
| 1200x703 | 1847x1082 | 1.998.454 | 1.54x |
| 749x468 | 1789x1118 | 2.000.102 | 2.39x |

Los tres convergen a ~2.000.000 px. El nivel "Prime" = 2 MP.
Los planes superiores amplían el presupuesto, no el factor.

Detalle → [[Logica-Dimensionado]]

## Límites de entrada observados

- Formatos: JPG, PNG, WebP
- Peso máximo: 50 MB

## Elementos de UI observados

- Zona de drag & drop grande, con enlace "explora" e importación desde Drive
- Galería persistente de trabajos, cada tarjeta con miniatura, "Antes: AxB px",
  "Después: CxD px", nivel usado y botón de descarga
- Selección múltiple por checkbox
- Modal de detalle: slider vertical sobre la imagen completa arriba, recorte al
  100% lado a lado abajo
- Botón "Reutilizar configuraciones"

Traducción a requisitos → [[Requisitos-UI]]

## Nota legal

Las capturas de referencia usan portadas de discos. Sirven para desarrollo, no
para material público del producto. #pendiente conseguir set de prueba propio o
de licencia libre.
