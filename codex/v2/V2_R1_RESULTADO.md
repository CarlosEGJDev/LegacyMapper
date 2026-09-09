# V2-R1 Resultado

## Estado

PASS

V2-R1 implementada como Call Graph Foundation. V2-R2 NO iniciada.

## Archivos modificados

- `legacy_documenter/models/evidence.py`
- `legacy_documenter/models/call.py`
- `legacy_documenter/models/__init__.py`
- `legacy_documenter/extractors/call_extractor.py`
- `legacy_documenter/analysis/call_resolver.py`
- `legacy_documenter/main.py`
- `tests/test_v1_unittest.py`
- `tests/fixtures/v2_r1_sample/App.vbproj`
- `tests/fixtures/v2_r1_sample/Page.vb`
- `tests/fixtures/v2_r1_sample/Servicio.vb`
- `codex/V2_R1_RESULTADO.md`

## Modelo implementado

- `Evidence`: archivo, línea, expresión, proyecto, clase y método cuando están disponibles.
- `TypeReference`: imports normales y aliases (`Imports Alias = Namespace.Tipo`).
- `Instantiation`: tipo textual, variable, clase/método contenedor, tipo resuelto y confianza.
- `Call`: expresión, receiver, método, cantidad de argumentos, clase/método contenedor, destino resuelto, proyecto destino, candidatos y confianza.

## Extracción

Patrones soportados en V2-R1:

- `Imports Namespace`
- `Imports Alias = Namespace.Tipo`
- `Dim servicio As New Servicio()`
- `Dim servicio As Servicio = New Servicio()`
- `New Servicio()`
- `obj.Metodo()`
- `Clase.Metodo()`
- `Me.Metodo()`
- `MyBase.Metodo()`
- `Metodo()`

El extractor registra método y clase contenedora usando análisis por líneas lógicas, sin interpretar cuerpos de método en profundidad.

## Resolución

Reglas de confianza:

- `confirmed`: el tipo o método destino se resuelve contra un único símbolo V1 compatible.
- `inferred`: llamada interna dentro de una clase cuando no existe símbolo miembro suficiente, pero la clase/método contenedor dan contexto local.
- `unresolved`: no hay evidencia suficiente o hay múltiples candidatos.

No se resuelve por coincidencia global simple de nombre de método.

## Nuevos índices

- `output/index/calls.json`
- `output/index/functional_dependencies.json`

Estos complementan `dependencies.json`; no lo reemplazan.

## Tests

- Comando: `python -m unittest discover -s tests`
- Total: 16 tests.
- Resultado: OK.
- Nuevos tests V2-R1: imports, instanciación, llamada por instancia, llamada Shared, llamada interna, llamada entre proyectos y llamada ambigua.

## Compatibilidad V1

V1 continúa funcionando. Los índices existentes se mantienen y se agregan índices nuevos compatibles.

Ejecuciones realizadas:

- `python -m unittest discover -s tests`: 16 tests OK.
- `python main.py tests/fixtures/v2_r1_sample --output output/v2_r1_fixture --verbose`: 3 archivos, 0 errores.
- `python main.py . --output output/v2_r1_internal --verbose`: 72 archivos, 0 errores.

## Limitaciones

- No resuelve sobrecargas por firma ni tipos de argumentos.
- No resuelve tipos por `Imports` todavía cuando el nombre corto tiene múltiples candidatos.
- No analiza eventos WebForms, Oracle, SQL ni stored procedures en V2-R1.
- No resuelve llamadas dinámicas, reflexión, late binding ni factories.
- Puede omitir llamadas con sintaxis VB.NET compleja no cubierta por los patrones iniciales.

## Riesgos

- Falsos positivos posibles en llamadas internas simples `Metodo()` dentro de expresiones complejas.
- Falsos negativos posibles en llamadas multilinea complejas o invocaciones sin paréntesis.
- Los nombres de métodos resueltos se normalizan internamente en minúscula en el target funcional inicial.

## Ejecución real recomendada

```powershell
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r1_full" --verbose
```

Revisar como mínimo:

- `output\v2_r1_full\index\repository.json`
- `output\v2_r1_full\index\projects.json`
- `output\v2_r1_full\index\symbols.json`
- `output\v2_r1_full\index\logical_symbols.json`
- `output\v2_r1_full\index\webforms.json`
- `output\v2_r1_full\index\dependencies.json`
- `output\v2_r1_full\index\errors.json`
- `output\v2_r1_full\index\calls.json`
- `output\v2_r1_full\index\functional_dependencies.json`

## Próximo paso

V2-R1 lista para validación sobre repositorio legacy real.

V2-R2 NO iniciada.
