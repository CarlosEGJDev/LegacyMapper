# Aceptación independiente del propietario — resultado final

Documento de ronda (histórico). Estado vigente: `PROJECT_STATE.json` (`owner_standalone_acceptance_final`).

```text
OWNER_STANDALONE_ACCEPTANCE = PASS        OWNER_MANUAL_REVIEW = PASS        BLOCKING_ACCEPTANCE_DEBT = 0
H5 = CLOSED    POST_V5 = CLOSED    V6 = NOT_STARTED
```

## Recorrido de la aceptación

| Etapa | Resultado |
| --- | --- |
| Instalación independiente | Wheel instalada no editable en un venv limpio, `PYTHONPATH` vacío, importación desde `site-packages`, sin depender del checkout (PASS) |
| Análisis IST real nuevo | Baseline fresco: 45 874 archivos, 91 soluciones, 228 proyectos, Evidence 1.0; sin reutilizar el baseline de H5 (PASS) |
| ACC-01 | La aceptación detectó que no existía interpretación jerárquica de sistema completo. Remediación R1: paquete `legacy_documenter/system/`, comandos `interpret-system` / `project-system`, identidad estable de solicitud, persistencia por intercambio, reanudación sin repetir llamadas, manifiesto de cobertura, verificación de cuenta. Commit `de0e822b7b02a60ffaa4447fd840b425795e8b77` |
| Ensayo con STUB | 597 solicitudes planificadas y completadas, 0 llamadas en la segunda corrida, 602 páginas, 0 defectos |
| Interpretación real del sistema completo | 597/597 solicitudes exitosas (SYSTEM 1, SOLUTION 85, PROJECT 184, VIEW 135, FLOW 72, DATA 120); 2 intentos fallidos transitorios por DNS, 2 reintentos, 0 interrupciones por cuota. Proveedor `copilot-local`, cuenta CarlosEGJDev, modelo por defecto del proveedor |
| Reanudación / repetición | Segunda corrida: 0 llamadas, 597 respuestas reproducidas, cobertura sin cambios |
| BD-1 (R2) | Las respuestas reales traían `CONFIRMED:` / `INFERRED:` / `UNRESOLVED:` en la prosa y llegaron a 191 páginas humanas. Corregido normalizando la prosa antes de persistir (registros nuevos) y de forma determinista en la proyección (597 registros existentes), preservando la identidad de solicitud: 0 llamadas, sin escáner, analizador ni lecturas de código |
| Producto humano y de máquina | 602 páginas, PDF válido; enlaces rotos 0, activos faltantes 0, JSON inválido 0, ids colgantes 0, ids duplicados 0, fugas de procedencia 0, estados humanos inválidos 0, prefijos de verdad en inglés 0, omisiones silenciosas 0 |
| Revisión manual del propietario | PASS |

## Cobertura final

```text
HUMAN_AND_MACHINE_DOCUMENTED = 183    MACHINE_ONLY_DOCUMENTED = 10    UNRESOLVED_NO_SOLUTION = 35
CONTROLLED_ERROR = 0                  PENDING_INTERPRETATION = 0
```

Deriva respecto al STUB (184/9): `WebAmbiente`. La IA real produjo solo afirmaciones no resueltas y la clasificación determinista lo dejó solo de máquina.
No es un defecto y no se forzó la igualdad.

## Pruebas

Suite completa: 3 626 pruebas, 0 fallos, 0 errores, 135 omitidas (15 pruebas nuevas de R2). Llamadas reales al proveedor durante la remediación: 0.

## Observaciones no bloqueantes

- `subject` vacío en 606 de 7 347 afirmaciones (DATA, FLOW, PROJECT, SOLUTION): `VALID_OPTIONAL`.
- Telemetría de tokens: `NOT_AVAILABLE_FROM_ADAPTER`; no se inventan cifras.
- Interpretación SYSTEM: estructurada y válida, fundamentada, sin invención de negocio ni inferencia de obsolescencia, con lo no resuelto preservado, legible.
  Los grupos ADH, COT, MED, PEN y SUB son agrupaciones documentales por prefijo de nombre, no dominios de negocio afirmados salvo que la evidencia lo respalde.

## Comentario del propietario

La documentación generada se considera excelente y útil para la versión actual. Parte del contenido es necesariamente inferido de la evidencia
disponible, y es aceptable porque la incertidumbre está representada. La reconstrucción visual de vistas y pantallas no se generó en este producto
final; queda diferida a una versión futura y no bloquea la aceptación.

## Mejoras futuras diferidas (no bloqueantes)

Extracción más profunda del repositorio · mayor cobertura de artefactos · reconstrucción visual de vistas/pantallas · validación futura de un
proveedor/benchmark local Qwen3 · posible enriquecimiento con SQL / procedimientos almacenados · ajuste adicional de la interpretación.

## Artefactos

La wheel candidata de R2 (`5baee7d9418da732e74ad651fe91b997c7bffac5736e100a4c749a9a9d9909ba`) se construyó desde un árbol sin commit y es solo evidencia
de verificación de R2. La wheel de lanzamiento final debe reconstruirse desde el SHA del checkpoint final.
