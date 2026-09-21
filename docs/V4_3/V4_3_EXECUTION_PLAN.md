# V4.3 — Plan de revisiones para Evidence Projection & Consumable Documentation

## Objetivo
V4.3 es la última versión funcional de consolidación de V4 antes de V5.

Debe convertir la evidencia determinista ya descubierta por LegacyMapper en información:
- útil para humanos;
- en español por defecto;
- compacta y navegable;
- trazable hasta FLOW/PATH/DAO/source;
- consumible por IA sin enviar contexto masivo;
- preparada para un futuro plugin mediante una proyección estable, sin implementar Plugin Runtime.

Principio rector:

> Python descubre; Python selecciona e hidrata; IA interpreta.

V5 queda reservado para el desacoplamiento grande:
- Core ↔ tecnología analizada;
- Core ↔ proveedor/modelo de IA;
- evidence model tecnológico neutral;
- adapters/capabilities multi-tecnología;
- Plugin Runtime posterior según decisión de alcance.

## Evidencia empírica externa
Las pruebas reales se realizaron exclusivamente en una copia de prueba fuera del repositorio de desarrollo:
- LegacyMapper de prueba: `C:\PruebasLegacyMapper\LegacyMapper`
- fuente real: `C:\inetpub\wwwroot\2010\IST\operacional`
- resultados: `C:\PruebasLegacyMapper\Resultados\prueba_01` / `prueba_02`
- scripts experimentales temporales: solo existen en la copia de prueba.

Esos scripts NO forman parte del producto, NO deben suponerse presentes en el repositorio que usa Claude y NO deben copiarse automáticamente al runtime.

Hallazgos empíricos convertidos en requisitos:
1. El análisis determinista del sistema real funciona.
2. Un contexto `SYSTEM` puede terminar en un prompt real de ~13.8 MB / ~3.6 M tokens aunque la estimación interna sea mucho menor.
3. Un contexto `FLOW` filtrado es pequeño, pero actualmente contiene principalmente referencias y no suficiente significado.
4. Una proyección FLOW hidratada experimental de ~5.6k tokens permitió una interpretación útil y trazable.
5. La IA debe recibir instrucciones explícitas de no usar herramientas y devolver solo la estructura requerida.
6. La documentación técnica actual es correcta pero algunas vistas siguen siendo demasiado grandes/planas para humanos.
7. La documentación humana debe ser español por defecto.
8. El detalle exhaustivo debe conservarse como evidencia, pero no dominar la vista humana principal.

## Casos reales de aceptación externa
### A. Consulta compleja con múltiples terminales
`webCobMorosidad\CobLiquidacionDeudaPrev.ascx` → `Load` → `Page_Load`

### B. Procesamiento/carga con terminales confirmados
`webCobMorosidad\cobCargaArcIntRea.ascx` → `Click` → `btnCargar_Click`

### C. Escritura/transacción
`webCobMorosidad\cobChqInsRen.ascx` → `Click` → `HypGuardar_Click`

### D. Flujo sin terminal confirmado
Ejemplo: `webCobMorosidad\CobConsultaTransferencia.ascx` → `Load` → `Page_Load`

Cada caso debe producir documentación útil de lo conocido, separar incertidumbre y conservar trazabilidad sin inventar comportamiento.

## Frontera de runtime
LegacyMapper runtime/product no puede depender de:
- `docs/`
- `prompts/`
- `codex/`
- `tests/`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`
- resultados históricos de rondas
- evidencia del piloto externo
- scripts experimentales creados en `C:\PruebasLegacyMapper`

## Orden obligatorio
R0 → R1 → R2 → R3 → R4 → R5 → R6 → R7 → Piloto real externo → R8 si hay correcciones → R9 cierre.

No ejecutar R9 hasta que el piloto real externo haya sido revisado y aprobado.
