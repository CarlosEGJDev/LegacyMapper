# Retomar LegacyMapper desde un clon limpio

Estado: vigente (post-H5). Suficiente para continuar desde cualquier ruta o máquina.

Marcadores: `<REPO_ROOT>` repositorio · `<WORK_ROOT>` workspace generado (desechable) ·
`<SOURCE_ROOT>` corpus fuente legado (solo lectura) · `<OUTPUT_ROOT>` salida de una corrida.

## Qué es

LegacyMapper analiza código legado de forma **determinista** (Python descubre y resuelve hechos), persiste
Evidence normalizada y, opcionalmente, deja que una IA proponga interpretaciones. Luego proyecta
documentación humana, paquetes para IA y vistas internas. La IA nunca decide.

## Estado actual

```text
H1-H5 = CLOSED      POST_V5 = CLOSED      BLOCKING_DEBT = 0      V6 = NOT_STARTED
```

Fuente de verdad: `PROJECT_STATE.json`. No hay prompt activo (`prompts/CURRENT/README.md`). H5 validó
IST real: 113 soluciones, 260 proyectos, un análisis determinista, 15 solicitudes reales de IA correctas.
Evidencia: `docs/POST_V5/H5_REAL_IST_VALIDATION_AND_CLOSURE_RESULT.md` y `..._EVIDENCE.json`.

## Arquitectura

`docs/ARCHITECTURE/CURRENT_ARCHITECTURE.md`: Source → análisis determinista → Evidence persistida → IA
opcional → conocimiento estructurado → proyecciones human / ai / internal.

## Instalación

```text
cd <REPO_ROOT>
python -m venv <WORK_ROOT>/venv
<WORK_ROOT>/venv/Scripts/pip install .          # sin dependencias obligatorias
legacymapper --help                              # o: python main.py --help
```

Python 3.11+ (probado con 3.14). El SDK del proveedor de IA es opcional.

## Estructura del repositorio

```text
legacy_documenter/   paquete del producto (runtime independiente)
tests/               unittest (perfiles por capacidad: devtest)
tools/               utilidades de desarrollo (no forman parte del runtime)
docs/                OPERATIONS, ARCHITECTURE (vigentes); V4..V5, POST_V5 (históricos)
prompts/CURRENT/     punto de entrada de prompts; prompts/archive/ = historia cerrada
PROJECT_STATE.json   estado operativo autoritativo
```

## Workspace

Ver `docs/OPERATIONS/WORKSPACE_CONTRACT.md`. Es generado y desechable; puede estar en cualquier ruta.

## Configuración de la fuente

La fuente se pasa como argumento; nunca se guarda en un archivo confirmado:
`python main.py full "<SOURCE_ROOT>" --output "<OUTPUT_ROOT>"`. Se valida (existe, legible, sin solaparse con
la salida) antes de escanear.

## Configuración del proveedor

Opcional. Sin SDK/configuración, `interpret` devuelve `PROVIDER_UNAVAILABLE` / `PROVIDER_CONFIGURATION_*`
sin escanear. Los tests nunca llaman a un proveedor real.

## Flujo operativo

```text
# 1. Análisis determinista (una vez)
python main.py full "<SOURCE_ROOT>" --output "<OUTPUT_ROOT>/baseline"

# 2. Reutilizar Evidence persistida (sin reescanear, sin IA)
python main.py docs     "<OUTPUT_ROOT>/baseline"
python main.py visuals  "<OUTPUT_ROOT>/baseline"

# 3. Interpretación de IA (opcional, puede llamar al proveedor)
python main.py interpret "<OUTPUT_ROOT>/baseline" --output "<OUTPUT_ROOT>/ai/<run>"

# 4. Paquete final humano (+ ai/internal)
python main.py deliver  "<OUTPUT_ROOT>/baseline" --output "<OUTPUT_ROOT>/package"
```

`deliver` produce un sitio HTML estático y PDFs (`DELIVERABLES_MANIFEST.json`). Proyectos sin UI generan
un paquete solo de máquina.

## Tests

`docs/OPERATIONS/TESTING_GUIDE.md`. Resumen:

```text
python -X utf8 -m legacy_documenter.devtest fast        # tras cada cambio pequeño
python -X utf8 -m legacy_documenter.devtest changed     # sugerencia según git status
python -X utf8 -m unittest discover -s tests            # solo hitos / release
```

IST real: solo por decisión explícita; defina `LEGACYMAPPER_REAL_IST_BASELINE` (y
`LEGACYMAPPER_SOURCE_ROOT` para `tools/`).

## Release / checkpoint

1. Suite completa en verde (0 fallos, 0 errores; los skips de integración externa traen razón).
2. `PROJECT_STATE.json` y el documento de resultado de la ronda actualizados.
3. Revisión del responsable; solo entonces commit / push / tag (nunca automáticos).

## Regenerar el workspace desechable

Borrar `<WORK_ROOT>` es seguro. Para reconstruirlo: paso 1 del flujo operativo (≈10 min sobre IST) y, si se
desea, `interpret` y `deliver`. Sin baseline previo el producto funciona igual.
