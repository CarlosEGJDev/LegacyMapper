# LegacyMapper V5.3 — R3 Verification + Real Regression

## 1. Objetivo

Verificar V5.3 de extremo a extremo sobre una baseline ya calibrada y estable.

R3 debe confirmar que el motor incremental/cache:

- preserva equivalencia canónica frente a full/off;
- cae de forma segura ante cache inválida/incompatible/corrupta;
- respeta los defaults aprobados;
- mantiene límites seguros de rutas y cache externa;
- no introduce regresiones en Evidence Core, IDs, documentación ni outputs;
- está listo para R4 de cierre.

R3 NO debe rediseñar V5.3.

NO iniciar R4.

---

## 2. Fuente de autoridad

Leer antes de actuar:

- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.md`
- `docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.json`
- `docs/V5/V5_3_R2_9_1_GIT_CHECKPOINT.md`
- `PROJECT_STATE.json`
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`
- `AGENTS.md`
- `CLAUDE.md`

Regla:

**R1 manda. R3 verifica; no inventa arquitectura nueva.**

---

## 3. Estado de partida

Checkpoint actual esperado:

`aa7db0db6c77d7ec8a1b15f50e33bf176d948bcd`

Defaults aprobados para V5.3:

- `cache-mode=auto`
- `verify-cache=fast`
- `trust-mtime=false`
- `incremental-max-changed-ratio=None`

Estado adicional:

`CHANGED_RATIO_DEFAULT_DEFERRED`

R2 está técnicamente completo.

V5.3 sigue abierta.

Pendiente esperado sin versionar:

`docs/V5/V5_3_R2_9_1_GIT_CHECKPOINT.md`

Antes de ejecutar, regularizar en continuidad la aprobación humana de R2.9/R2.9.1 si los documentos aún quedaron en `PENDING`.

---

# PARTE A — PREFLIGHT

## 4. Verificación de baseline

Antes de tocar código:

- confirmar rama `main`;
- confirmar HEAD esperado;
- confirmar backup branch;
- confirmar working tree;
- revisar cambios no versionados;
- confirmar que no existen cambios runtime inesperados;
- confirmar que IST oficial permanece sin modificación.

No hacer commit/push/tag.

---

## 5. Reusar evidencia, no repetir calibración

R3 NO debe repetir:

- rejilla completa de changed ratio;
- 33 corridas de R2.9;
- medición de punto de equilibrio;
- diseño de defaults.

R2.9 ya cubre eso.

Usar esa evidencia como baseline.

Solo repetir pruebas necesarias para verificación/regresión R3.

---

# PARTE B — REGRESIÓN CANÓNICA

## 6. Referencia full/off

Generar o reutilizar una referencia válida `off/full`.

Comparar con el comparador aprobado:

`tools/v5_3_compare_full_incremental.py`

Validar contra:

- auto cold;
- auto warm;
- refresh;
- verify fast;
- verify hash;
- cache externa warm.

Criterio:

- 0 added;
- 0 removed;
- 0 changed;

fuera de exclusiones contractuales ya aprobadas.

No ampliar exclusiones.

---

## 7. Determinismo

Ejecutar al menos dos corridas equivalentes warm independientes sobre el mismo input.

Verificar:

- outputs deterministas byte a byte;
- mismo número de archivos;
- mismos hashes;
- manifests coherentes;
- cache válida;
- no cambio de IDs.

`repository.json`/RUN_SUMMARY y exclusiones ya contractuales se tratan como tales; no inventar nuevas excepciones.

---

# PARTE C — RECUPERACIÓN ANTE CACHE INVÁLIDA

## 8. Matriz de fallos obligatoria

Validar de manera controlada:

1. manifest ausente;
2. manifest JSON corrupto;
3. checksum de `file_state` incorrecto;
4. `file_state` corrupto;
5. un shard corrupto con `verify=fast`;
6. un shard corrupto con `verify=hash`;
7. más de un shard corrupto;
8. extraction cache schema mismatch;
9. analyzer/version/fingerprint mismatch;
10. repository identity mismatch;
11. analysis config mismatch;
12. cache directory borrado entre corridas.

Para cada caso registrar:

- session mode;
- fallback_reason;
- hits/misses;
- si la cache se autocura;
- si la ejecución termina SUCCESS;
- equivalencia con full/off.

La regla principal:

**ante duda, recomputar; nunca reutilizar evidencia incompatible.**

---

## 9. Interrupción / manifest-last

Probar o revalidar que una corrida interrumpida/no completada:

- no deja manifest final válido;
- no se reutiliza como cache válida en la siguiente corrida;
- la siguiente corrida cae a full/cold seguro;
- termina generando cache sana.

Puede usarse fixture/control de tests si provocar interrupción real sobre IST es innecesariamente costoso.

---

# PARTE D — CACHE EXTERNA Y LÍMITES DE RUTA

## 10. Cache externa

Verificar:

- cold externa;
- warm externa;
- borrar cache externa y regenerar;
- repo identity protege contra otro repo;
- no aparecen rutas absolutas sensibles en métricas;
- output canónico no depende de que cache sea interna o externa.

---

## 11. Junction / reparse point real en Windows

R2.9 dejó explícitamente pendiente este caso.

Si el entorno lo permite sin privilegios peligrosos:

crear un junction/reparse point controlado en un directorio temporal y validar que `resolve_cache_dir`:

- resuelve el destino real;
- rechaza cache que termine dentro del repo;
- rechaza cache que contenga repo/output cuando corresponde;
- no borra contenido ajeno;
- no escapa del directorio autorizado.

Si Windows/política/sandbox no permite crear un reparse point real:

documentar:

`WINDOWS_REPARSE_REAL_TEST_NOT_AVAILABLE`

y cubrir la lógica con test dirigido de resolución de paths.

No bloquear R3 únicamente por falta de privilegio del entorno si la lógica ya está cubierta y el riesgo queda explícito.

---

# PARTE E — SEGURIDAD / INVARIANTES

## 12. Invariantes funcionales

Confirmar explícitamente:

- Evidence Core idéntico;
- IDs preservados;
- confirmed/inferred/unresolved preservados;
- resolvers globales siguen recomputando;
- scope sigue observacional;
- no stage skipping;
- no partial resolver recomputation;
- no flow cache;
- no projection cache;
- `artifacts.json` sigue diferido;
- `trust-mtime` sigue false por defecto;
- ratio sigue `None`;
- verify sigue `fast`;
- cache-mode sigue `auto`.

---

## 13. Sanitización

Revalidar:

- records que cambian al sanitizar siguen bypass;
- no se persisten secretos en extraction cache;
- métricas no contienen rutas absolutas externas ni contenido sensible;
- corrupción no fuerza dump de contenido sensible en errores.

No hacer búsqueda destructiva sobre IST.

---

# PARTE F — PERFORMANCE REGRESSION CHECK

## 14. Performance

No recalibrar.

Medir solo:

- auto warm;
- refresh;
- off/full;
- verify hash directo si se ejecuta.

Comparar con R2.9 y R2.8.

No exigir igualdad de wall-clock.

Marcar alerta si aparece regresión sustancial e inexplicada, por ejemplo:

- warm pierde claramente la ventaja esperada;
- extraction cache deja de dar hits;
- write-skip deja de saltar outputs idénticos;
- verify hash crece de forma desproporcionada.

Si hay variación por I/O, documentarla sin inventar causalidad.

---

# PARTE G — TESTS

## 15. Tests dirigidos nuevos

Agregar tests solo para huecos reales de R3.

Prioridades:

- corruption/fallback matrix;
- interrupted session / manifest-last;
- external cache path safety;
- reparse/junction si puede automatizarse;
- determinismo;
- equivalencia;
- defaults finales.

Evitar duplicar decenas de tests ya existentes.

---

## 16. Suite completa

Ejecutar:

`python -X utf8 -m unittest discover -s tests`

Criterio:

- 0 failures;
- 0 errors.

Registrar:

- total;
- skips;
- duración.

---

# PARTE H — IST REAL

## 17. Uso mínimo de IST

R3 debe usar IST, pero con el mínimo número razonable de corridas.

Objetivo:

**verificar, no volver a medir toda V5.3.**

Plan recomendado:

1. full/off de referencia;
2. auto cold o cache regenerada;
3. auto warm;
4. refresh;
5. verify hash;
6. cache externa warm;
7. una o dos corridas de recuperación controlada si realmente necesitan IST.

El resto puede probarse con fixtures si la semántica ya está cubierta.

Reutilizar outputs válidos cuando sea seguro y trazable.

---

# PARTE I — DEUDA

## 18. Clasificar deuda final de V5.3

Usar:

- BLOCKING;
- CLOSURE_REQUIRED;
- FUTURE_PHASE;
- OBSERVATION.

Revisar:

- junction/reparse real;
- full_pipeline.py VERY_HIGH;
- artifacts.json diferido;
- scope conservador;
- no partial resolver;
- no projection/flow cache;
- two atomic writers;
- repository.json no determinista;
- changed ratio default diferido;
- trust-mtime opt-in inseguro.

Nada FUTURE_PHASE debe convertirse en bloqueo de R4 sin evidencia contractual.

---

# PARTE J — CONTINUIDAD

## 19. PROJECT_STATE

Si R3 queda verde, actualizar:

- latest_completed_round = V5.3-R3;
- latest_approved_round = V5.3-R2.9.1 o equivalente según esquema;
- round_status = READY_FOR_HUMAN_REVIEW;
- next_round = V5.3-R4;
- V5.3 closed = false;
- R3 verification = completed;
- defaults finales preservados;
- changed ratio default deferred.

No declarar V5.3 cerrada.

---

## 20. Continuity docs

Actualizar solo estado vigente y ledger.

No reescribir historia.

Incluir R2.9.1 y R3.

---

# PARTE K — GIT

## 21. Git

Solo consultas.

NO:

- commit;
- push;
- tag;
- amend;
- rebase;
- clean;
- reset destructivo.

Registrar:

- branch;
- HEAD;
- ahead de origin/main;
- backup;
- archivos modificados/nuevos;
- pendientes anteriores.

---

# PARTE L — FUERA DE ALCANCE

## 22. No implementar

NO:

- R4;
- V5.4;
- partial resolver recomputation;
- stage skipping;
- projection cache;
- flow cache;
- artifacts.json;
- nuevos scope modes;
- cambios Evidence Core;
- cambios de IDs;
- IA;
- push/tag.

R3 verifica. No expande.

---

# PARTE M — ENTREGABLE

## 23. Documento

Crear:

`docs/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md`

Debe incluir:

1. Objetivo.
2. Estado inicial.
3. Evidencia R2 reutilizada.
4. Archivos modificados.
5. Matriz de regresión canónica.
6. Determinismo.
7. Matriz de cache inválida.
8. Interrupción/manifest-last.
9. Cache externa.
10. Junction/reparse.
11. Seguridad/sanitización.
12. Invariantes.
13. Performance regression check.
14. Tests dirigidos.
15. Suite completa.
16. Corridas IST ejecutadas.
17. Equivalencia.
18. Deuda final.
19. PROJECT_STATE.
20. Continuidad.
21. Git.
22. Recomendación R4.
23. Estado final.

---

## 24. Estados finales permitidos

Si todo lo obligatorio pasa:

`V5_3_R3_READY_FOR_HUMAN_REVIEW`

Si queda un defecto de corrección/equivalencia/fallback seguro:

`V5_3_R3_BLOCKED`

Si el único hueco es no poder ejecutar junction/reparse real por restricción del entorno:

`V5_3_R3_READY_FOR_HUMAN_REVIEW`
+
`WINDOWS_REPARSE_REAL_TEST_NOT_AVAILABLE`

---

## 25. Criterio de cierre

R3 está lista si:

- equivalencia full/incremental confirmada;
- determinismo confirmado;
- corrupción/incompatibilidad recuperan de forma segura;
- cache externa segura;
- límites de ruta verificados;
- suite completa verde;
- IST real verificado sin repetir calibración;
- no hay deuda BLOCKING;
- continuidad apunta a R4;
- V5.3 sigue abierta hasta aprobación humana y cierre formal.

Detenerse para revisión humana.
