# LegacyMapper V5 — Create Final Tag `v5`

## Objetivo
Crear y publicar el tag final `v5` sobre el commit formal de cierre:

`e831a2f84d2749b4452e06860521b3171093c7b9`

Autorización humana explícita: crear y publicar el tag `v5`.

## Preflight
Ejecutar:
- `git status -sb`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git ls-remote origin refs/heads/main`
- `git tag --list`
- `git show-ref --tags`

Requerido:
- branch `main`
- HEAD = origin/main = remote main = `e831a2f84d2749b4452e06860521b3171093c7b9`
- ahead 0 / behind 0
- `v5` no existe local ni remoto

Si falla: `V5_TAG_CREATION_BLOCKED`.

## Convención
Inspeccionar `v5.2`:
- `git cat-file -t v5.2`
- `git for-each-ref refs/tags/v5.2 --format="%(refname) %(objecttype) %(objectname) %(subject)"`
- `git show --no-patch --decorate v5.2`

Replicar exactamente la convención:
- si `v5.2` es lightweight, crear `v5` lightweight;
- si es annotated, crear `v5` annotated con mensaje `LegacyMapper V5 final release baseline`.

## Crear
Apuntar explícitamente a:
`e831a2f84d2749b4452e06860521b3171093c7b9`

No taggear HEAD implícitamente.

## Verificar local
- `git rev-list -n 1 v5`
- `git show --no-patch --decorate v5`

Debe resolver al commit de cierre.

## Push
Ejecutar solo:
`git push origin v5`

Sin force. No push de `main`.

## Verificación remota
- `git ls-remote --tags origin refs/tags/v5 refs/tags/v5^{}`
- `git rev-list -n 1 v5`
- `git status -sb`

Estado final:
- `V5_TAG_CREATED`
- `V5_TAG_PUSHED_TO_ORIGIN`
- `tag = v5`
- `target = e831a2f84d2749b4452e06860521b3171093c7b9`
- `tag_type = <lightweight|annotated>`

No commit, amend, rebase, reset, clean, force, ni otros tags.
