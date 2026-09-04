---
tipo: tecnico
estado: resuelto
actualizado: 2026-09-04
---

# Lógica de dimensionado

## Problema

Dada una imagen de AxB y un presupuesto de N megapíxeles, calcular las
dimensiones enteras de salida que maximizan el uso del presupuesto sin
excederlo, manteniendo la relación de aspecto.

## Fórmula (asimétrica, no simplificar)

```
escala      = sqrt(presupuesto_px / (ancho * alto))
lado_largo  = floor(lado_largo_original * escala)
lado_corto  = round(lado_largo * relacion_de_aspecto_original)
```

El lado largo se **trunca**, el lado corto se **deriva y redondea**. Truncar
ambos lados falla en 749x468. Redondear ambos falla en 1200x703. Solo esta
combinación reproduce los tres casos medidos contra la referencia real.

Consecuencia aceptada: el área puede exceder el presupuesto en centenas de
píxeles (`1789x1118 = 2.000.102`, +102 sobre 2 MP). Es el comportamiento de
la referencia, no un bug. `strict=True` existe para quien necesite garantía
dura, y difiere del resultado por defecto.

## Casos de validación (medidos, no tocar)

| Entrada | Salida |
|---|---|
| 736x416 | 1881x1063 |
| 1200x703 | 1847x1082 |
| 749x468 | 1789x1118 |

## Consecuencia para el pipeline

El modelo de super-resolución trabaja a factor entero (2x, 4x). El objetivo casi
nunca es entero. Por lo tanto: inferir a 4x y luego reducir al objetivo exacto
con Lanczos. Reducir da mejor resultado que interpolar hacia arriba.

Implementación → `engine/sizing.py` (fuente de verdad del código, no del vault).
Pipeline completo → [[Pipeline]]
