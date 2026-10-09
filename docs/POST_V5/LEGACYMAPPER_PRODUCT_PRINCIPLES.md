# LegacyMapper — Principios del producto

Principios estables, independientes de la historia de versiones. Si un cambio los contradice, el cambio está mal o el principio debe revisarse explícitamente con autoridad humana.

> LegacyMapper reconstruye la comprensión práctica más fiable posible de cómo funciona un sistema legado, usando evidencia determinista primero e interpretación de IA después, sin inventar hechos en silencio.

1. **Hechos deterministas antes que interpretación.** Python descubre, estructura, selecciona y valida; la IA interpreta.
2. **Nunca inventar relaciones faltantes.**
3. **Preservar confirmed / inferred / unresolved.** Lo no resuelto no se promueve a confirmado sin evidencia determinista.
4. **La provenance es parte del producto.** Toda afirmación importante traza a evidencia o se marca como interpretación.
5. **Analizar una vez, proyectar muchas.** Evidence normalizada y persistida; las vistas y la IA la reutilizan.
6. **La comprensión humana es una salida de primera clase.** Correcto no basta: debe entenderse, por audiencia.
7. **La salida de IA es una propuesta** hasta que un humano la aprueba.
8. **El conocimiento canónico requiere autoridad humana explícita.** Nada se aprueba ni canoniza automáticamente.
9. **El runtime es independiente de los archivos de desarrollo y gobernanza** (verificado fuera del repo de desarrollo).
10. **La validación en un sistema real es obligatoria** antes de afirmar que una arquitectura está completa.

Corolarios: ningún provider real se invoca por accidente; el análisis es estático (no ejecuta el código analizado); la fuente legada es de solo lectura; identidad lógica del repositorio ≠ ruta física.
