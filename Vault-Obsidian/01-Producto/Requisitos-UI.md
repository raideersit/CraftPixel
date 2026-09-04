---
tipo: producto
estado: borrador
actualizado: 2026-09-04
---

# Requisitos de UI

## Pantalla 1 — Subida

- Drag & drop grande + selector de archivos
- Acepta JPG, PNG, WebP hasta 50 MB
- Selector de nivel de salida (2 MP / 4 MP / 8 MP)
- Muestra la resolución de salida calculada ANTES de procesar

## Pantalla 2 — Galería

- Grilla de trabajos previos, persistente entre sesiones
- Cada tarjeta: miniatura, "Antes: AxB px", "Después: CxD px", nivel, descarga
- Checkbox por tarjeta para acciones en lote
- Menú de tres puntos por tarjeta: descargar, borrar, reutilizar config

## Pantalla 3 — Modal de detalle

- Arriba: imagen completa con slider vertical antes/después
- Abajo: recorte al 100% lado a lado, para ver el detalle real
- Etiquetas de dimensiones sobre cada mitad
- Botones: "Reutilizar configuraciones", descargar, compartir

## Transversal

- Indicador de progreso real, alimentado por el backend. No animación falsa.
- Errores explícitos: archivo muy pesado, formato no soportado, sin memoria,
  timeout. Cada uno con mensaje distinto y acción sugerida.

## Enlaces

- De dónde salen estos requisitos → [[Referencia-LetsEnhance]]
