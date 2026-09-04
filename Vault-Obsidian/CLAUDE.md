# Mejorador de Imágenes

App web de super-resolución con IA. El usuario sube una imagen y recibe una
versión ampliada y nítida. Referencia de producto: LetsEnhance.io.

Documentación viva en el vault de Obsidian: `Desktop/U/Mejorador-Imagenes/Vault-Obsidian/`.
El vault es la fuente de verdad del **producto**. Este archivo es la fuente de
verdad del **código**. No dupliques contenido entre los dos: enlaza.

## Regla que define el producto

La salida NO usa factor fijo. Se calcula por presupuesto de megapíxeles
manteniendo la relación de aspecto. Nivel base = 2.000.000 px exactos.

El algoritmo es **asimétrico** y esto no es negociable ni "simplificable":

1. `scale = sqrt(presupuesto / (w*h))`
2. el **lado largo** se trunca (`floor`)
3. el **lado corto** se deriva del lado largo con la relación de aspecto exacta
   y se **redondea** (`round`)

Truncar ambos lados falla en 749x468. Redondear ambos falla en 1200x703.
Solo esta combinación reproduce los tres casos medidos.

Consecuencia aceptada: el área puede exceder el presupuesto en centenas de
píxeles (`1789x1118 = 2.000.102`, +102). Es el comportamiento de la referencia.
El modo `strict=True` existe para quien necesite garantía dura, y difiere.

Casos de regresión (no tocar, están medidos contra la referencia real):

| Entrada | Salida |
|---|---|
| 736x416 | 1881x1063 |
| 1200x703 | 1847x1082 |
| 749x468 | 1789x1118 |

Implementación: `engine/sizing.py`. Si cambiás esa función, corré
`python3 engine/sizing.py` antes de commitear. Sale con código 1 si falla un caso.

## Pipeline

`detectar tipo de imagen -> elegir modelo -> inferencia 4x -> Lanczos al objetivo exacto`

- Bajar con Lanczos siempre; subir con Lanczos solo si evita una segunda pasada 4x.
- Tiles con solapamiento para imágenes grandes. Las costuras son un bug, no un
  detalle cosmético.
- `engine/sizing.py:plan()` decide cuántas pasadas 4x hacen falta.

## Restricciones del proyecto

- Uso propio, no comercial. Sin restricción de licencia: modelos con
  cláusula no-comercial (ej. CodeFormer) están permitidos.
- **Avisá siempre si una decisión implica costo recurrente** (GPU en la nube,
  API de terceros) y ofrecé la alternativa autohospedada.
- No proponer dependencia final de LetsEnhance ni de otro servicio cerrado.
  Sirve solo como prototipo desechable.
- El worker no debe saber dónde corre, aunque hoy solo corra en PC local.
  Mismo contenedor serviría en VPS o serverless si algún día hace falta.

## Convenciones de código

- Python 3.11+. Type hints en las firmas públicas. `dataclass(frozen=True)`
  para los objetos de plan y configuración.
- Nada de pseudocódigo ni fragmentos sueltos: archivos completos con ruta.
- Errores explícitos con tipo propio, no `Exception` genérica:
  archivo muy pesado, formato no soportado, VRAM agotada, timeout.
- Los tres casos de dimensionado se validan en cada cambio del motor.

## Cómo hablarme

- Español latinoamericano neutro, directo, sin preámbulos.
- Cuando haya opciones: tabla breve (opción / ventaja / costo / dificultad) y
  después la recomendación con la razón.
- Si falta información crítica, preguntá lo mínimo. No asumas en silencio.
- Manejo Python, Node.js y Linux. No expliques lo básico de esos temas.

## Reglas para el vault de Obsidian (MCP)

- Leé el vault libremente.
- **No escribas en el vault sin mostrarme antes qué vas a cambiar.**
- Una nota = un tema. Si una nota pasa de 60 líneas, se divide.
- Las decisiones cerradas van a un ADR en `03-Decisiones/`, nunca a la bitácora.
- `CONTEXTO.md` tiene un tope de 40 líneas. Para agregar algo ahí, sacá otra cosa.
- `#pendiente` marca lo que falta. Buscá ese tag al empezar una sesión.

## Estado

Fase: implementación del pipeline. `ADR-001` cerrado: todo corre local en
PC (GTX 1050, 2 GB VRAM), sin servidor ni túnel.

El dimensionado ya está resuelto y validado en `engine/sizing.py`. No lo
vuelvas a derivar.

Motor: `realesrgan-ncnn-vulkan` (no la versión PyTorch — VRAM limitada),
tiles obligatorios (`--tile 128` o `192`). Rostros: GFPGAN o CodeFormer,
con fallback a CPU si no entra en VRAM.
