---
tipo: tecnico
estado: borrador
actualizado: 2026-09-04
---

# Pipeline de procesamiento

```
imagen entrada
   ↓
validar (formato, peso, dimensiones)
   ↓
detectar tipo (foto / ilustración / con rostros)
   ↓
elegir modelo → [[Modelos-IA]]
   ↓
inferencia a 4x
   ├─ si la imagen es grande: procesar por tiles con solapamiento
   └─ el solapamiento evita costuras visibles en las uniones
   ↓
[opcional] restauración de rostros
   ↓
redimensionar al objetivo exacto con Lanczos → [[Logica-Dimensionado]]
   ↓
codificar salida (PNG o JPG con control de calidad)
   ↓
guardar + notificar progreso
```

## Requisitos no funcionales

- Cola asíncrona: el usuario no queda bloqueado esperando
- Progreso real reportado por etapa, no simulado
- Errores tipificados: peso, formato, VRAM agotada, timeout

## Puntos de riesgo

- Costuras en los bordes de los tiles → ajustar solapamiento
- Agotamiento de VRAM en imágenes grandes → limitar tamaño de tile
- Rostros deformados por el upscaler general → orden correcto de los pasos
