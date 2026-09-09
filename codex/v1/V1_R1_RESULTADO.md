# V1-R1 Resultado

## Resumen

- Estado general: PASS.
- V1-R1 implementada como revisión correctiva acotada.
- V2 NO iniciada.

## Archivos modificados

- `legacy_documenter/config.py`
- `legacy_documenter/scanner/repository_scanner.py`
- `legacy_documenter/models/symbol.py`
- `legacy_documenter/extractors/vbnet_extractor.py`
- `legacy_documenter/extractors/webforms_extractor.py`
- `legacy_documenter/analysis/dependency_resolver.py`
- `legacy_documenter/main.py`
- `tests/test_v1_unittest.py`
- `codex/V1_R1_RESULTADO.md`

## R1-01

- Implementación: la resolución de atributos de directivas ASP.NET ahora usa una vista normalizada case-insensitive.
- Se preserva el diccionario original `attributes` como evidencia.
- Los registros `Register` conservan sus atributos originales y agregan `_normalized` para resolución interna.
- Tests: variantes `CodeBehind`, `Codebehind`, `codebehind`; además `Inherits`, `Src`, `Namespace` y `Assembly`.
- Resultado: PASS.

## R1-02

- Implementación: el scanner excluye por defecto cualquier carpeta cuyo nombre empiece por `_vti_`.
- La exclusión queda registrada en `repository.ignored`.
- Tests: fixture con `Real.vbproj` real y `_vti_cnf/Real.vbproj` inválido.
- Resultado: PASS, sin falso error XML.

## R1-03

- Implementación: los símbolos VB.NET mantienen `namespace` y agregan `declared_namespace`, `root_namespace`, `effective_namespace`, `project_path` y `namespace_confidence`.
- Modelo elegido: `namespace` conserva compatibilidad; `effective_namespace` representa el namespace compilado cuando existe evidencia determinista.
- Método de asociación: únicamente por `Compile Include` declarado en `.vbproj`, resolviendo la ruta relativa desde el proyecto.
- Casos no resolubles: si un `.vb` no está incluido en un único `.vbproj`, no se asigna `RootNamespace` ni `effective_namespace` inventado.
- Resultado: PASS.

## R1-04

- Implementación: se agrega `logical_symbols` como índice compatible adicional.
- Método: consolida `Partial Class` por nombre, `effective_namespace` y `project_path`; conserva todas las declaraciones físicas en `symbols`.
- Tratamiento de ambigüedades: cuando falta proyecto/namespace, el símbolo lógico queda con confianza `unresolved`; no se eliminan símbolos físicos.
- Resultado: PASS.

## Tests

- Comando ejecutado: `python -m unittest discover -s tests`
- Tests ejecutados: 12.
- Resultado: OK.

## Ejecución interna

- Comando ejecutado: `python main.py . --output output/v1_r1_internal --verbose`
- Resultado: 59 archivos procesados, 0 errores.

## Compatibilidad

- No se eliminan campos existentes de JSON.
- Se agrega el índice `logical_symbols.json` y nuevos campos compatibles en `symbols.json`.
- CLI, scanner, extractores, dependencias y documentación Markdown continúan funcionando.

## Limitaciones

- No se implementa análisis funcional profundo.
- No se resuelven llamadas entre clases, SQL, stored procedures ni flujo Web -> BL -> DAL.
- La consolidación parcial no fusiona símbolos no parciales ni casos ambiguos sin evidencia suficiente.

## Próximo paso

V1-R1 lista para prueba contra repositorio legacy real.

V2 NO iniciada.

Comando recomendado:

```powershell
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v1_r1_full" --verbose
```
