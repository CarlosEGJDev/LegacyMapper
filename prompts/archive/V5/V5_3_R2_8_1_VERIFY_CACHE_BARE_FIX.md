# LegacyMapper V5.3 — R2.8.1 Fix de `--verify-cache` bare

## 1. Objetivo
Corregir un único defecto detectado en la revisión humana de R2.8:

`--verify-cache` sin valor debe equivaler inequívocamente a `--verify-cache=hash` y **nunca consumir el siguiente argumento posicional**.

Esta ronda es correctiva y mínima. NO iniciar R2.9.

## 2. Estado de partida
R2.8 terminó como `V5_3_R2_8_READY_FOR_REVIEW`, pero la revisión humana detectó un defecto pequeño en la interfaz CLI.

Estado Git según el informe R2.8:
- rama `main`;
- HEAD `dae2ba5`;
- 4 commits por delante de `origin/main`;
- sin commit/tag/push de R2.8;
- cambios de R2.8 aún sin versionar;
- pendientes también:
  - `prompts/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`
  - `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`

No hacer commit en esta ronda.

## 3. Defecto a corregir
R2.8 implementó:

`--verify-cache[={fast,hash}]`

con:
- default `fast`
- bare `--verify-cache` = `hash`

Pero el informe documenta que un bare antes de un argumento posicional puede intentar consumir ese posicional como valor.

## 4. Semántica final requerida
- flag ausente → `verify_cache = fast`
- bare `--verify-cache` → `verify_cache = hash`, sin consumir el token siguiente
- `--verify-cache=hash` → `hash`
- `--verify-cache=fast` → `fast`
- `--verify-cache=foo` → error de parser claro

No aceptar semántica ambigua basada en la posición del flag.

## 5. Implementación preferida
Resolver la ambigüedad en la capa CLI, no en runtime/cache.

Preferencia:
- normalizar `argv` antes de `argparse`;
- token exacto `--verify-cache` se convierte internamente en `--verify-cache=hash`;
- no inspeccionar ni consumir el token siguiente.

Esto permite conservar:
- `--verify-cache=fast`
- `--verify-cache=hash`
- default `fast`
- parser/router existentes.

Si existe una solución más limpia y pequeña con la infraestructura CLI actual, puede usarse.

NO modificar:
- `cache/verify.py`;
- algoritmo fast/hash;
- fallback;
- File State;
- extraction cache;
- scope;
- write-skip;
- R1 contract.

## 6. Evitar side effects
La normalización de `argv` debe:
- afectar únicamente el token exacto `--verify-cache`;
- no tocar `--verify-cache=fast` ni `--verify-cache=hash`;
- no tocar valores posicionales que contengan texto parecido;
- conservar orden;
- ser determinista;
- no depender del filesystem.

Preferir helper pequeño y testeable.

## 7. Casos obligatorios de parser
Añadir tests para:
1. flag ausente → `fast`;
2. bare al final → `hash`;
3. bare antes del primer posicional → `hash` y posicional intacto;
4. bare entre posicionales si la sintaxis CLI lo permite;
5. bare antes de otro flag;
6. `--verify-cache=hash`;
7. `--verify-cache=fast`;
8. `--verify-cache=foo` → error;
9. path llamado `hash` no es consumido por el bare;
10. path llamado `fast` no es consumido por el bare;
11. path con espacios;
12. `analyze` sigue sin aceptar estos controles si R2.8 así lo definió;
13. router sigue mapeando `hash`/`fast` 1:1 a `run_full_pipeline`.

Los casos 9 y 10 son importantes: el parser no debe decidir mirando si el token siguiente coincide con un choice.

## 8. Tests de regresión R2.8
Ejecutar al menos:
- `tests/test_v5_3_r2_8_cache_cli_controls.py`
- nuevo/ajustado test de R2.8.1 si se separa;
- tests del parser/router relacionados;
- `git diff --check`.

No es necesario repetir las corridas IST A–H si:
- el diff es exclusivamente parser/argv normalization/tests/docs;
- runtime recibe exactamente el mismo valor `verify_cache`;
- no cambia `cache/verify.py` ni comportamiento de pipeline.

## 9. Smoke test CLI real
Ejecutar comandos reales sobre fixture pequeño o repo de tests:

A. `full <posicionales> --verify-cache`
- parse correcto
- `verify_cache=hash`

B. `full --verify-cache <posicionales>`
- parse correcto
- posicionales intactos
- `verify_cache=hash`

C. `full <posicionales> --verify-cache=fast`
- `fast`

D. `full <posicionales> --verify-cache=hash`
- `hash`

No necesita pipeline IST completo; puede interceptarse/verificarse el mapping router→biblioteca.

## 10. Suite completa
No es obligatoria si el cambio queda estrictamente limitado al parser y todos los tests dirigidos pasan.

Si se toca cualquier código runtime/cache:
`python -m unittest discover -s tests`

## 11. Documentación R2.8
Actualizar:
`docs/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`

Eliminar la deuda que decía:
`--verify-cache sin valor antes de un posicional lo consumiría como valor`

y registrar que bare ya es inequívoco.

No alterar las demás conclusiones/mediciones IST.

## 12. Entregable R2.8.1
Crear:
`docs/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`

Debe incluir:
1. defecto;
2. causa;
3. solución;
4. archivos modificados;
5. semántica final;
6. tests nuevos/ajustados;
7. smoke tests;
8. tests dirigidos;
9. confirmación de que runtime/cache no cambió;
10. impacto sobre informe R2.8;
11. Git;
12. estado final.

## 13. Git
Solo consultas.

NO:
- commit;
- push;
- tag;
- amend;
- rebase;
- reset;
- clean.

Registrar:
- rama;
- HEAD;
- archivos modificados/nuevos;
- pendientes documentales de R2.7.1/R2.8.

## 14. Fuera de alcance
NO:
- R2.9;
- cambiar defaults de cache;
- cambiar `verify=fast/hash`;
- cambiar `trust-mtime`;
- cambiar ratio;
- cambiar cache-dir;
- cambiar scope;
- optimizar rendimiento;
- repetir IST completo innecesariamente;
- commit/push/tag.

## 15. Estado final permitido
Si el defecto queda corregido:
`V5_3_R2_8_1_READY_FOR_REVIEW`

Si no puede garantizarse que el bare preserve los posicionales:
`V5_3_R2_8_1_BLOCKED`

## 16. Criterio de cierre
R2.8.1 está lista si:
- bare `--verify-cache` = `hash`;
- nunca consume el siguiente posicional;
- `=fast` y `=hash` siguen funcionando;
- inválidos fallan;
- router recibe el valor correcto;
- runtime/cache no cambia;
- tests dirigidos verdes;
- informe R2.8 actualizado;
- no se amplió alcance.

Detenerse para revisión humana.
