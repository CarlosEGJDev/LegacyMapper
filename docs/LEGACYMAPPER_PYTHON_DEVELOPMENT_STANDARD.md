# Estándar de desarrollo Python de LegacyMapper

## Principio rector

LegacyMapper se implementa siguiendo buenas prácticas de Python. Cuando una convención de C# entra en conflicto con Python idiomático, prevalecen las buenas prácticas de Python. La organización conceptual debe seguir siendo familiar para un desarrollador C# sin imitar construcciones que no aportan valor.

El límite permanente es: **Python descubre y resuelve hechos; el LLM interpreta; el humano aprueba**.

## Nombres y organización

- Clases: `PascalCase`; módulos y funciones: `snake_case`; constantes: `UPPER_SNAKE_CASE`.
- Un módulo debe tener una responsabilidad comprensible. Una clase principal por archivo es preferible cuando la clase tiene entidad propia, no para DTO pequeños relacionados.
- Use `models`, `services`, `validators`, `providers`, `analysis`, `documentation`, `knowledge`, `security` o `utils` solo si describen una responsabilidad real.
- No introduzca Repository, Factory, Strategy, Mediator, contenedores DI o Protocols sin una necesidad concreta.

## Funciones, métodos y tipos

- Las funciones públicas y límites entre servicios deben tener entradas, salidas y efectos explícitos.
- Prefiera funciones cohesionadas, validaciones tempranas y poca anidación.
- Use type hints modernos compatibles con la versión de Python del proyecto. Limite `Any` a fronteras inevitables.
- Use `dataclass`, `Enum`, `TypedDict`, `Protocol` o Pydantic solo cuando simplifiquen el contrato. No migre modelos estables por estética.

## Docstrings y comentarios

- Toda clase y función pública, y todo helper interno significativo, debe tener un docstring breve que explique propósito, resultado y efectos no obvios.
- Los comentarios explican por qué existe una restricción: determinismo, seguridad, trazabilidad, inmutabilidad o límite LLM. No narran sintaxis evidente.

## Validación y errores

- La evidencia inválida se rechaza; nunca se repara, promueve o degrada silenciosamente.
- Use excepciones de dominio cuando ayuden a distinguir fallos recuperables de violaciones contractuales.
- No use `except Exception` salvo en un límite externo deliberado; documente el motivo y devuelva un error seguro.
- Los estados, límites de tokens y valores canónicos deben tener un propietario único cuando compartirlos no rompa compatibilidad.

## Logging

- Registre etapa, artefacto afectado, causa del fallo y si hubo llamada a proveedor.
- Nunca registre secretos, credenciales, connection strings, tokens ni payloads sensibles.
- Evite logging por cada registro si no aporta diagnóstico operativo.

## Determinismo, LLM y proveedores

- Discovery, resolución, selección de evidencia, presupuestos, validación y serialización son responsabilidades de Python.
- El LLM no crea identidades canónicas ni convierte evidencia ausente en hechos.
- El comportamiento específico de proveedor permanece bajo `legacy_documenter/llm/providers/`.
- No coloque decisiones semánticas dependientes de un modelo concreto. Provider y model efectivos son telemetría.
- El runtime no depende de `codex/`, ChatGPT ni prompts manuales de desarrollo.

## Seguridad e inmutabilidad

- El repositorio legado es de solo lectura.
- Toda evidencia exportada debe pasar por sanitización centralizada.
- No copie secretos a errores, logs, manuales o proyecciones.
- Los artefactos canónicos de rondas aprobadas son entradas inmutables para rondas posteriores.
- Una limitación aceptada sigue siendo una limitación; no es el hecho faltante.

## Pruebas

- Cada cambio conserva la suite existente y añade casos para contratos nuevos.
- Los nombres describen comportamiento esperado. No debilite assertions para obtener PASS.
- Las pruebas que generan artefactos deben usar temporales o restaurar el estado en `finally`.
- Antes de entregar ejecute `python -m unittest discover -s tests`.
- Para cambios de readiness, vuelva a ejecutar `python -m legacy_documenter.knowledge.readiness` y confirme `READY`, `AI_KNOWLEDGE_ALLOWED=true` y `AI_KNOWLEDGE_GENERATED=false`.

## Compatibilidad y refactoring

- Conserve entry points públicos; use wrappers pequeños cuando mueva una implementación.
- Refactorice incrementalmente: inventario, riesgo, cambio acotado, pruebas focales y regresión completa.
- No elimine código sin comprobar referencias de runtime, pruebas, documentación y generación canónica. Ante duda, consérvelo y registre deuda técnica.
- La reducción de líneas no es un objetivo. Cohesión, legibilidad, contratos explícitos y seguridad sí lo son.

