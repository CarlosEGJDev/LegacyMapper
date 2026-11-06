# LegacyMapper V5.3 — R2.8 Modos y Controles CLI de Cache

## 1. Objetivo

Exponer de forma segura y coherente en CLI los controles de caché definidos por V5.3 R1 y ya soportados parcial o internamente por R2.4–R2.7.

Esta ronda debe convertir el comportamiento incremental existente en una interfaz operable y verificable por el usuario, sin cambiar la semántica de corrección.

Objetivos:

1. exponer `cache_mode`;
2. exponer `cache_dir`;
3. implementar/verificar `verify_cache`;
4. implementar `trust_mtime` solo si R1 lo autoriza y con semántica segura;
5. implementar `incremental_max_changed_ratio` solo si R1 lo define;
6. mantener fallback conservador;
7. reflejar correctamente los modos en `RUN_METRICS.json`;
8. mantener equivalencia con full.

NO iniciar R2.9.

---

## 2. Fuente de autoridad

Leer antes de modificar:

- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_4_CACHE_MANIFEST_AND_FILE_STATE.md`
- `docs/V5/V5_3_R2_5_EXTRACTION_CACHE.md`
- `docs/V5/V5_3_R2_6_WRITE_SKIP_REMAINING_OUTPUTS.md`
- `docs/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`
- `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

### Regla contractual

Si R1 define nombres, defaults o semántica diferentes a este prompt:

**R1 manda.**

Documentar cualquier diferencia en el informe.

---

## 3. Estado de partida

R2.7 dejó:

- File State persistido;
- extraction cache adoptada;
- guardián del contrato;
- write-skip por bytes;
- `RUN_METRICS.json`;
- scope conservador;
- `scope` no controla stages;
- resolvers/proyecciones se recomputan;
- parámetros de biblioteca existentes:
  - `cache_mode`;
  - `cache_dir`;
  - `extraction_cache`;
- CLI aún sin controles V5.3.

Checkpoint de R2.7:

`dae2ba5083bf3c6f863106456e201f0c4e55ab42`

Pendientes documentales:

- prompt R2.7.1;
- resultado R2.7.1.

NO hacer commit en esta ronda.

---

# PARTE A — CONTRATO CLI

## 4. Recuperar contrato R1

Antes de implementar, crear en el informe una tabla:

| Opción | Nombre R1 | Default R1 | Semántica R1 | Implementación previa | Acción R2.8 |
|---|---|---|---|---|---|
| cache mode | ... | ... | ... | biblioteca | ... |
| cache dir | ... | ... | ... | biblioteca | ... |
| verify cache | ... | ... | ... | parcial/implícita | ... |
| trust mtime | ... | ... | ... | no | ... |
| changed ratio | ... | ... | ... | no | ... |

No inventar opciones nuevas fuera de R1.

---

## 5. `--cache-mode`

Preferencia si coincide con R1:

```text
--cache-mode {auto,off,refresh}
```

Semántica esperada:

### auto

- comportamiento normal;
- valida caché;
- reutiliza extraction cache si es compatible;
- File State/diff activos;
- write-skip activo;
- fallback full ante incompatibilidad.

### off

- no leer caché;
- no reutilizar extraction cache;
- no depender de File State previo;
- no escribir caché V5.3;
- pipeline sigue produciendo salida completa;
- write-skip de outputs puede seguir activo si contractualmente no depende de `_cache_v53/`;
- métricas de cache pueden quedar ausentes o reflejar `off` según R1.

### refresh

- ignorar reutilización previa;
- ejecutar como full;
- reconstruir una caché nueva al finalizar SUCCESS;
- nunca tratar cache previa como autoridad.

No añadir todavía modos `changed/project/component/folder` si R1 los deja para otra fase.

---

## 6. `--cache-dir`

Exponer ruta explícita de caché.

Default:

`<output>/_cache_v53/`

salvo que R1 diga otra cosa.

Requisitos:

- aceptar ruta relativa/absoluta según contrato;
- normalizar de forma determinista;
- si es externa a output:
  - no incluirla en outputs/product manifests;
  - no mezclar repositorios;
  - repository identity sigue validándose;
- crear directorio solo cuando corresponda;
- `off` no debe crearla.

### Seguridad

- no permitir que un manifest redirija arbitrariamente a otra ruta;
- `file_state.path` sigue cerrado;
- evitar traversal accidental;
- no borrar directorios externos completos;
- solo gestionar archivos propios de `_cache_v53`.

---

## 7. `--verify-cache`

Implementar según R1.

Objetivo esperado:

forzar validación exhaustiva de la caché persistida antes de reutilizar.

Debe aclarar qué verifica:

- `CACHE_MANIFEST.json`;
- checksum de `file_state.json`;
- checksums de shards;
- schema/versiones;
- repository identity;
- config fingerprint;
- extraction cache schema.

Si el comportamiento normal ya verifica todo esto, determinar si `--verify-cache`:

- añade una comprobación más profunda;
- verifica todos los shards aunque no vayan a usarse;
- o es redundante y debe mapearse a una operación diagnóstica.

NO crear una falsa opción que no cambie nada sin documentarlo.

Si R1 define esta opción como comando/flag diagnóstico, respetarlo.

---

## 8. `--trust-mtime`

Esta opción es delicada.

### Regla principal

No habilitar una optimización insegura.

R2.4 estableció que `mtime_ns` es metadata y no participa de igualdad.

Si R1 autoriza `--trust-mtime`, implementar exactamente sus garantías.

Semántica segura sugerida solo si coincide con R1:

- opt-in explícito;
- default false;
- permitir evitar hashing SOLO cuando:
  - path coincide;
  - size coincide;
  - `mtime_ns` coincide;
  - estado previo es válido;
  - repository identity/config/version compatibles;
- cualquier duda → hash real;
- nunca usarlo con cache corrupta/incompatible;
- documentar que el usuario acepta riesgo de mtimes restaurados/manipulados.

### Test crítico

Cambiar bytes, conservar size y restaurar mtime:

- con `trust_mtime=false` → debe detectar cambio;
- con `trust_mtime=true` → documentar exactamente la semántica contractual esperada.

Si R1 no lo autoriza aún:

NO implementarlo y declarar:

`TRUST_MTIME_DEFERRED_BY_CONTRACT`

---

## 9. `--incremental-max-changed-ratio`

Implementar solo si R1 lo define.

Objetivo:

si demasiados archivos cambiaron, evitar trabajo incremental que no aporta beneficio y ejecutar full.

Semántica esperada:

```text
changed_ratio =
(modified + added + deleted) / previous_file_count
```

o la fórmula exacta de R1.

Requisitos:

- rango validado;
- default contractual;
- threshold claramente documentado;
- si ratio supera threshold:
  - reutilización incremental desactivada;
  - full seguro;
  - caché puede regenerarse tras SUCCESS;
  - razón visible en métricas/fallback_reason;
- rename sigue contando como added+deleted salvo contrato distinto.

No usar este threshold para saltar resolvers/proyecciones.

---

# PARTE B — PARSER Y CLASIFICACIÓN

## 10. Parser CLI

Agregar únicamente opciones autorizadas por R1.

Actualizar el guardián introducido en R2.3 que clasifica todas las opciones CLI.

Clasificación esperada:

- `cache_mode`: runtime/cache-control;
- `cache_dir`: output/cache-location;
- `verify_cache`: runtime/cache-control;
- `trust_mtime`: runtime/cache-control con impacto en estrategia de File State;
- `incremental_max_changed_ratio`: runtime/cache-control.

No incluirlas en `ANALYSIS_CONFIG_FINGERPRINT` salvo que R1 lo exija.

Razón:

cambian estrategia/reuso, no significado semántico del análisis.

---

## 11. Comando `full`

Los nuevos flags deben funcionar al menos en:

`main.py full`

No ampliar automáticamente a `analyze` si el contrato no lo exige.

Recordatorio:

hasta R2.7, `analyze` no usa la caché V5.3.

Si R1 exige soporte en `analyze`, implementar y justificar.

---

## 12. API de biblioteca

Mantener compatibilidad con:

`run_full_pipeline(...)`

Evitar duplicar semántica entre parser y API.

CLI debe mapear a los mismos parámetros internos.

No crear dos implementaciones paralelas.

---

# PARTE C — COMPORTAMIENTO Y FALLBACK

## 13. Matriz de modos

Construir tests y documentación para:

| Caso | auto | off | refresh |
|---|---|---|---|
| sin cache | cold/full | full sin cache | full + nueva cache |
| cache válida | incremental | full sin reuse | full + reemplazo |
| cache corrupta | fallback full | ignorada | ignorada/reemplazada |
| repo mismatch | fallback full | ignorada | full + cache del repo actual |
| analyzer mismatch | fallback full | ignorada | full + nueva |
| extraction schema mismatch | full extraction + autocuración | sin reuse | full + nueva |

Usar vocabulario exacto de R1/R2.7 en métricas.

---

## 14. `RUN_METRICS.json`

Actualizar solo lo necesario para reflejar controles CLI.

Debe registrar:

- mode;
- session_mode;
- fallback_reason;
- cache_dir lógico/relativo si es seguro, o un indicador `external_cache_dir` sin persistir ruta absoluta si hay riesgo;
- verify_cache enabled/disabled;
- trust_mtime enabled/disabled si existe;
- max_changed_ratio y observed_changed_ratio si existe.

No persistir secretos ni rutas absolutas innecesarias.

No convertir métricas en configuración de entrada.

---

## 15. Scope

R2.8 NO cambia la semántica de scope.

Mantener:

- `.vb/.aspx/.ascx/.master/.vbproj/.sln` conservadores/full cuando corresponda;
- cierre transitivo solo como observabilidad/suelo;
- no stage skipping;
- no invalidación parcial.

Tests explícitos deben asegurar que los nuevos flags no convierten scope en compuerta de ejecución.

---

# PARTE D — TESTS

## 16. Tests de parser

Cubrir:

1. defaults;
2. `--cache-mode auto`;
3. `off`;
4. `refresh`;
5. valor inválido;
6. `--cache-dir`;
7. ruta con espacios;
8. verify flag;
9. trust-mtime si aplica;
10. ratio válido;
11. ratio fuera de rango;
12. guardián de clasificación CLI.

---

## 17. Tests de comportamiento

Cubrir:

### auto

- cold;
- warm;
- corrupt;
- incompatible;
- repo mismatch.

### off

- no lectura de cache;
- no escritura de cache;
- extraction completa;
- outputs equivalentes;
- no crea cache_dir nuevo.

### refresh

- ignora cache válida;
- extraction completa;
- persiste nueva cache tras SUCCESS;
- fallo de corrida no deja manifest válido.

### external cache dir

- funciona;
- identidad protege repositorios;
- no entra en output manifest;
- borrar cache externa no afecta outputs.

### verify

- corrupción detectada;
- comportamiento diagnóstico/estricto según contrato.

### trust mtime

si se implementa:
- default seguro;
- bytes cambiados con mtime restaurado;
- opt-in contractual.

### changed ratio

si se implementa:
- debajo del threshold;
- igual al threshold;
- sobre threshold;
- previous count = 0;
- rename;
- fallback reason.

---

## 18. Equivalencia

Para todas las variantes:

- `auto`;
- `off`;
- `refresh`;
- cache interna;
- cache externa;
- verify;

comparar outputs deterministas contra full/reference.

Objetivo:

0 diferencias.

---

# PARTE E — IST

## 19. Validación IST obligatoria

Repositorio:

`C:\Users\cgalianj\source\IST_40\Operacional`

No modificar IST oficial.

### A. auto cold

- cache nueva;
- full;
- metrics correctas.

### B. auto warm

- cache reuse;
- extracción warm;
- write-skip.

### C. off

- misma salida;
- no reuse;
- no escritura de cache.

### D. refresh

- misma salida;
- full;
- cache regenerada.

### E. external cache dir

Usar directorio temporal fuera de output.

- cold;
- warm;
- borrar;
- regenerar.

### F. corrupt + verify

Corromper copia de cache, no cache oficial.

- fallback seguro;
- no error fatal salvo que R1 defina modo diagnóstico estricto.

### G. changed ratio

Si se implementa:
- copia de IST;
- cambios suficientes para quedar bajo/sobre threshold;
- verificar selección de modo.

### H. trust mtime

Si se implementa:
- copia;
- cambiar bytes;
- restaurar size/mtime;
- demostrar comportamiento exacto.

---

## 20. Rendimiento

Medir overhead de parser/control despreciable.

Para `verify-cache`, medir costo real en IST.

Para `trust-mtime`, si existe:

- medir ahorro;
- no adoptarlo por default.

Para max changed ratio:

- demostrar que no añade coste relevante.

---

# PARTE F — SEGURIDAD Y MANTENIBILIDAD

## 21. Seguridad

Revisar:

- cache-dir externo;
- path traversal;
- symlinks/reparse points si relevantes en Windows;
- no borrar directorios ajenos;
- no seguir paths del manifest;
- corruption fallback;
- atomicidad;
- no secretos en metrics;
- `off` realmente independiente.

---

## 22. Mantenibilidad

Evitar:

- inflar más `full_pipeline.py`;
- semántica duplicada en parser/router/session;
- condicionales dispersos por stages.

Preferir un objeto/config coherente si ya existe patrón en repo.

No hacer refactor grande no necesario.

---

## 23. Suite completa

Ejecutar:

`python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

Criterio:

0 fallas, 0 errores.

---

# PARTE G — GIT Y DOCUMENTACIÓN

## 24. Git

Solo consultas.

NO:

- commit;
- push;
- tag;
- amend;
- rebase.

Registrar:

- rama;
- HEAD;
- commits ahead of origin;
- rama backup;
- archivos modificados/nuevos;
- prompt/documento R2.7.1 pendientes.

---

## 25. PROJECT_STATE

No actualizar salvo que la convención del proyecto exija hacerlo en cada ronda.

Si no:

documentar que se mantiene hasta checkpoint/cierre correspondiente.

---

# PARTE H — FUERA DE ALCANCE

## 26. No implementar

No:

- iniciar R2.9;
- stage skipping;
- partial resolver recomputation;
- persistent flow cache;
- projection cache;
- `artifacts.json`;
- nuevos IDs;
- cambios Evidence Core;
- cambios semánticos de documentación;
- nuevos scope modes `project/component/folder` salvo obligación explícita de R1;
- IA;
- push/tag.

---

# PARTE I — ENTREGABLE

## 27. Documento

Crear:

`docs/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`

Debe incluir:

1. Objetivo.
2. Contrato R1 recuperado.
3. Diferencias R1 vs prompt.
4. Opciones CLI implementadas.
5. Defaults.
6. Semántica `auto/off/refresh`.
7. `cache-dir`.
8. `verify-cache`.
9. `trust-mtime` implementado o diferido.
10. changed ratio implementado o diferido.
11. Clasificación CLI/fingerprints.
12. API biblioteca.
13. RUN_METRICS.
14. Scope invariants.
15. Tests parser.
16. Tests comportamiento.
17. Suite completa.
18. IST auto cold.
19. IST auto warm.
20. IST off.
21. IST refresh.
22. IST external cache.
23. IST verify/corrupt.
24. IST trust-mtime si aplica.
25. IST changed ratio si aplica.
26. Equivalencia.
27. Rendimiento.
28. Seguridad.
29. Mantenibilidad.
30. Deuda técnica.
31. Riesgos.
32. Fuera de alcance.
33. Estado Git.
34. Recomendación R2.9.
35. Estado final.

---

## 28. Estados finales permitidos

Si los controles quedan correctos y seguros:

`V5_3_R2_8_READY_FOR_REVIEW`

Si alguna opción contractual debe diferirse:

`V5_3_R2_8_READY_FOR_REVIEW`

más uno o más:

- `TRUST_MTIME_DEFERRED_BY_CONTRACT`
- `CHANGED_RATIO_DEFERRED_BY_CONTRACT`
- `VERIFY_CACHE_DEFERRED_BY_CONTRACT`

Si hay regresión, ambigüedad contractual, corrupción insegura o tests fallidos:

`V5_3_R2_8_BLOCKED`

---

## 29. Criterio de cierre

R2.8 está lista si:

- CLI refleja el contrato R1;
- defaults son seguros;
- `off` realmente desactiva cache;
- `refresh` reconstruye;
- cache-dir externo es seguro;
- verify tiene semántica real;
- trust-mtime no degrada seguridad silenciosamente;
- threshold no afecta corrección;
- scope sigue sin gobernar stages;
- outputs equivalentes;
- suite verde;
- IST validado;
- no se amplió alcance.

Detenerse para revisión humana.
