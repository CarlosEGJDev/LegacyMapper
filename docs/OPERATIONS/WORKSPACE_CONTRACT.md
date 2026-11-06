# Workspace contract

Estado: vigente (post-H5). Documento operativo, no histórico.

## Tres lugares, ninguna ubicación relativa obligatoria

| Lugar | Rol | Contenido | Ciclo de vida |
| --- | --- | --- | --- |
| **Repositorio** (`<REPO_ROOT>`) | Autoridad | Código, configuración, tests, docs, plantillas | Versionado en Git |
| **Workspace** (`<WORK_ROOT>`) | Estado generado | Baselines, respuestas de IA persistidas, paquetes, logs, venvs | **Desechable**: se puede mover o borrar |
| **Corpus fuente** (`<SOURCE_ROOT>`) | Entrada del usuario | Código legado analizado | **Solo lectura**; nunca se modifica ni se copia al repositorio |

Los tres pueden estar en cualquier parte, con espacios y caracteres Unicode. Ningún test ni módulo
activo puede suponer dónde están: reciben cada ubicación por argumento de CLI o variable de entorno.

## Reglas

1. El repositorio **no** depende de la ubicación física del workspace.
2. El producto funciona sin ningún baseline previo: un análisis nuevo lo regenera.
3. Las respuestas de proveedor de IA nunca son necesarias para la operación determinista.
4. Ningún test activo lee rutas absolutas de máquina, carpetas históricas de salida ni snapshots externos,
   salvo los marcados `REAL_IST` / `EXTERNAL_INTEGRATION`, que reciben su ubicación por configuración y
   se omiten (skip con razón explícita) si no está configurada.
5. Los reportes históricos pueden conservar rutas históricas; los documentos operativos usan marcadores
   (`<REPO_ROOT>`, `<WORK_ROOT>`, `<SOURCE_ROOT>`, `<OUTPUT_ROOT>`).

## Variables de entorno (solo integraciones externas)

| Variable | Uso |
| --- | --- |
| `LEGACYMAPPER_REAL_IST_BASELINE` | Directorio de un baseline determinista real (activa los tests `REAL_IST`) |
| `LEGACYMAPPER_SOURCE_ROOT` | Corpus fuente real, para herramientas manuales en `tools/` |
| `LEGACYMAPPER_EVIDENCE_OUTPUT` | Salida de `tools/v5_1_r2_real_ist_regression.py` |

## Estructura recomendada del workspace

```text
<WORK_ROOT>/
    Current/
        state/
            baseline/        un único baseline determinista canónico (opcional, regenerable)
            ai/              respuestas de IA persistidas, deduplicadas por SHA-256
        reference/
            final_human_sample/   muestra humana aprobada (opcional)
        README.md
    Archive/                 solo lo retenido a propósito
```

Mover el workspace: copiar o renombrar la carpeta y pasar la nueva ruta a los comandos. No hay rutas
absolutas guardadas dentro del baseline que impidan relocalizarlo para `docs`, `visuals`, `deliver` o
`interpret`.

## Regenerar el workspace desechable

```text
python main.py full "<SOURCE_ROOT>" --output "<WORK_ROOT>/Current/state/baseline"
```
