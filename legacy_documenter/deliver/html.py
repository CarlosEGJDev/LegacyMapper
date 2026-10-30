"""Deterministic static HTML rendering of the shared block model (post-V5 H4).

No framework, no CDN, no external fonts: relative links, UTF-8, semantic markup, keyboard-reachable `<details>` sections and
a tiny optional local script (table filter + title search). Status labels are always printed as text; the badge styling only
adds a border pattern, so the epistemic status survives grayscale printing.
"""
from __future__ import annotations

import posixpath
import re
from html import escape

from .markdown import Bullets, Callout, Code, Details, Figure, Heading, Para, Quote, Rule, Run, Table, plain

STATUS_CLASS = {
    "Confirmado": "confirmed", "Inferido (regla estructural)": "inferred", "Inferido (regla)": "inferred", "Inferido": "inferred",
    "No resuelto": "unresolved", "Interpretación de IA (no aprobada)": "ai", "Canónico (aprobado por una persona)": "canonical",
    "CONFIRMADO": "confirmed", "INFERIDO": "inferred", "NO RESUELTO": "unresolved", "IA - NO APROBADA": "ai", "CANÓNICO": "canonical",
}
STATUS_ORDER = ("CONFIRMED", "INFERRED", "UNRESOLVED", "AI_INTERPRETATION", "CANONICAL")
STATUS_CLS = {"CONFIRMED": "confirmed", "INFERRED": "inferred", "UNRESOLVED": "unresolved", "AI_INTERPRETATION": "ai", "CANONICAL": "canonical"}
STATUS_TEXT = {
    "CONFIRMED": "Confirmado", "INFERRED": "Inferido (regla estructural)", "UNRESOLVED": "No resuelto",
    "AI_INTERPRETATION": "Interpretación de IA (no aprobada)", "CANONICAL": "Canónico (aprobado por una persona)",
}
STATUS_MEANING = {
    "CONFIRMED": "Lo demuestra el código analizado.",
    "INFERRED": "Deducido con una regla estructural; no es una afirmación de negocio.",
    "UNRESOLVED": "El análisis no pudo determinarlo. No significa ausencia.",
    "AI_INTERPRETATION": "Propuesta de IA que ninguna persona ha aprobado. No es un hecho.",
    "CANONICAL": "Aprobado explícitamente por una persona.",
}
STATUS_PATTERN = {
    "CONFIRMED": "borde continuo", "INFERRED": "borde discontinuo", "UNRESOLVED": "borde punteado y marca «!»",
    "AI_INTERPRETATION": "doble borde y marca «IA»", "CANONICAL": "borde grueso y marca «OK»",
}


def _cls_for_text(text: str) -> str | None:
    t = text.strip()
    if t in STATUS_CLASS:
        return STATUS_CLASS[t]
    if t.startswith("Estado:"):
        low = t.lower()
        for key, cls in (("no resuelto", "unresolved"), ("confirmado", "confirmed"), ("inferido", "inferred")):
            if key in low:
                return cls
    return None


def rel(from_page: str, target: str) -> str:
    path, _, frag = target.partition("#")
    base = posixpath.dirname(from_page) or "."
    out = posixpath.relpath(path, base) if path else ""
    return out + (f"#{frag}" if frag else "")


_WORD = re.compile(r"\S{14,}")
_SOFT = re.compile(r"(?<=[\/._\-])(?=[^\/._\-])|(?<=[a-z0-9])(?=[A-Z])")


def soft_breaks(text: str) -> str:
    """Escaped text where long identifiers / routes may wrap after separators (dot, slash, backslash, underscore) and at camelCase boundaries (`<wbr>`), never mid-word."""
    out: list[str] = []
    last = 0
    for m in _WORD.finditer(text):
        out.append(escape(text[last:m.start()]))
        out.append("<wbr>".join(escape(p) for p in _SOFT.split(m.group(0)) if p))
        last = m.end()
    out.append(escape(text[last:]))
    return "".join(out)


def render_runs(runs: list[Run], page: str) -> str:
    text = plain(runs)
    cls = _cls_for_text(text) if len(text) < 80 else None
    parts: list[str] = []
    for r in runs:
        body = soft_breaks(r.text)
        if r.code:
            body = f"<code>{body}</code>"
        if r.bold:
            body = f"<strong>{body}</strong>"
        if r.italic:
            body = f"<em>{body}</em>"
        if r.href and not r.missing:
            if "://" in r.href:
                body = f'<a href="{escape(r.href, quote=True)}" rel="noopener">{body}</a>'
            else:
                body = f'<a href="{escape(rel(page, r.href), quote=True)}">{body}</a>'
        elif r.missing:
            body = f'<span class="ref-missing" title="Referencia fuera de este paquete">{body}</span>'
        parts.append(body)
    out = "".join(parts)
    if cls:
        return f'<span class="st st-{cls}">{out}</span>'
    return out


def render_figure(fig: Figure, page: str, *, heading_level: int = 3) -> str:
    counts = " · ".join(f"{STATUS_TEXT[s]}: {fig.status_counts[s]}" for s in STATUS_ORDER if fig.status_counts.get(s))
    partial = ""
    if fig.partial.get("partial"):
        partial = (f'<p class="note">Parcial: {fig.partial["included_count"]} elementos mostrados y {fig.partial["omitted_count"]} agregados '
                   f'en nodos de resumen; ninguno se descarta (el detalle está en el modelo JSON).</p>')
    children = ""
    if fig.children:
        items = "".join(f'<li><a href="{escape(rel(page, c_page), quote=True)}">{escape(c_title)}</a></li>' for c_title, c_page in fig.children)
        children = f'<details class="detail-links"><summary>Diagramas de detalle ({len(fig.children)})</summary><ul>{items}</ul></details>'
    role = '<span class="tag">resumen</span> ' if fig.role == "summary" else ('<span class="tag">detalle</span> ' if fig.role == "detail" else "")
    unresolved = f" · {fig.unresolved_nodes} nodos no resueltos" if fig.unresolved_nodes else ""
    return (
        f'<figure class="diagram"><a class="diagram-link" href="{escape(rel(page, fig.svg), quote=True)}" target="_blank" rel="noopener">'
        f'<img src="{escape(rel(page, fig.svg), quote=True)}" width="{fig.width}" height="{fig.height}" '
        f'alt="{escape(fig.title, quote=True)}" loading="lazy"></a>'
        f'<figcaption>{role}<strong>{escape(fig.title)}</strong><br>{escape(fig.kind)} · {fig.nodes} nodos · {fig.edges} relaciones'
        f'{unresolved}<br><span class="muted">{escape(counts)}</span><br>'
        f'<a href="{escape(rel(page, fig.page), quote=True)}">Abrir página del diagrama</a> · '
        f'<a href="{escape(rel(page, fig.svg), quote=True)}" target="_blank" rel="noopener">Abrir SVG a tamaño completo</a> · '
        f'<a href="{escape(rel(page, fig.model), quote=True)}">Modelo JSON</a></figcaption>{partial}{children}</figure>'
    )


def _render_block(b, page: str, out: list[str]) -> None:
    if isinstance(b, Heading):
        level = min(6, max(1, b.level))
        hcls = f' class="{escape(b.cls, quote=True)}"' if b.cls else ""
        out.append(f'<h{level} id="{escape(b.anchor, quote=True)}"{hcls}>{render_runs(b.runs, page)}</h{level}>')
    elif isinstance(b, Para):
        cls = f' class="{escape(b.cls, quote=True)}"' if b.cls else ""
        out.append(f"<p{cls}>{render_runs(b.runs, page)}</p>")
    elif isinstance(b, Quote):
        inner: list[str] = []
        for x in b.blocks:
            _render_block(x, page, inner)
        out.append("<blockquote>" + "".join(inner) + "</blockquote>")
    elif isinstance(b, Bullets):
        out.append("<ul>" + "".join(f"<li>{render_runs(i, page)}</li>" for i in b.items) + "</ul>")
    elif isinstance(b, Table):
        filt = ' data-filter="1"' if len(b.rows) > 12 else ""
        head = "".join(f'<th scope="col">{render_runs(h, page)}</th>' for h in b.headers)
        rows = "".join("<tr>" + "".join(f"<td>{render_runs(c, page)}</td>" for c in row) + "</tr>" for row in b.rows)
        cap = f"<caption>{escape(b.caption)}</caption>" if b.caption else ""
        out.append(f'<div class="table-wrap" tabindex="0"{filt}><table>{cap}<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
    elif isinstance(b, Code):
        out.append(f"<pre><code>{escape(b.text)}</code></pre>")
    elif isinstance(b, Rule):
        out.append("<hr>")
    elif isinstance(b, Figure):
        out.append(render_figure(b, page))
    elif isinstance(b, Callout):
        inner = []
        for x in b.blocks:
            _render_block(x, page, inner)
        title = f'<p class="callout-title">{escape(b.title)}</p>' if b.title else ""
        status = ' data-status="AI_INTERPRETATION"' if b.kind == "ai" else ""
        out.append(f'<aside class="callout callout-{escape(b.kind)}"{status}>{title}{"".join(inner)}</aside>')
    elif isinstance(b, Details):
        inner = []
        for x in b.blocks:
            _render_block(x, page, inner)
        out.append(f'<details{" open" if b.open else ""}><summary>{escape(b.summary)}</summary>{"".join(inner)}</details>')
    else:  # pragma: no cover - the block set is closed
        raise TypeError(type(b).__name__)


def render_blocks(blocks: list, page: str, *, sections: bool = True) -> str:
    """H2 sections become collapsible `<details open>` (all open by default; nothing is hidden)."""
    h2 = sum(1 for b in blocks if isinstance(b, Heading) and b.level == 2)
    out: list[str] = []
    group: list[str] | None = None

    def close() -> None:
        nonlocal group
        if group is not None:
            out.append("".join(group) + "</details>")
            group = None

    for b in blocks:
        if sections and h2 >= 3 and isinstance(b, Heading) and b.level <= 2:
            close()
            if b.level == 2:
                group = [f'<details class="sec" open><summary><h2 id="{escape(b.anchor, quote=True)}">{render_runs(b.runs, page)}</h2></summary>']
                continue
        target: list[str] = []
        _render_block(b, page, target)
        if group is not None:
            group.extend(target)
        else:
            out.extend(target)
    close()
    return "\n".join(out)


def legend_html() -> str:
    rows = "".join(
        f'<li><span class="st st-{STATUS_CLS[s]}">{escape(STATUS_TEXT[s])}</span> — {escape(STATUS_MEANING[s])} '
        f'<span class="muted">En diagramas: {escape(STATUS_PATTERN[s])}.</span></li>'
        for s in STATUS_ORDER
    )
    return f'<ul class="legend">{rows}</ul>'


NAV = (("index.html", "Inicio", ""), ("executive/index.html", "Ejecutivo", "executive"), ("functional/index.html", "Funcional", "functional"),
       ("technical/index.html", "Técnico", "technical"), ("deliverables/index.html", "Entregables", "deliverables"),
       ("deliverables/KNOWN_UNRESOLVED_AREAS.html", "No resuelto", "unresolved"), ("about.html", "Sobre la evidencia", "about"))


def page_shell(*, title: str, body: str, page: str, section_key: str, crumbs: list[tuple[str, str | None]], toc: list[tuple[str, str, int]],
               system_name: str = "", extra_head: str = "", available: set[str] | None = None) -> str:
    root = posixpath.relpath(".", posixpath.dirname(page) or ".")
    root = "" if root == "." else root + "/"
    current = ' aria-current="page"'
    nav = "".join(f'<li><a href="{root}{href}"{current if key == section_key else ""}>{label}</a></li>' for href, label, key in NAV
                  if available is None or href in available)
    crumb_html = " › ".join(
        f'<a href="{escape(rel(page, href), quote=True)}">{escape(label)}</a>' if href else f'<span aria-current="page">{escape(label)}</span>'
        for label, href in crumbs
    )
    toc_items = "".join(f'<li class="toc-{lvl}"><a href="#{escape(a, quote=True)}">{escape(t)}</a></li>' for a, t, lvl in toc)
    toc_html = (f'<aside class="toc" aria-label="En esta página"><details open><summary>En esta página</summary><ul>{toc_items}</ul></details></aside>'
                if toc else "")
    mini = " · ".join(f'<span class="st st-{STATUS_CLS[s]}">{escape(STATUS_TEXT[s])}</span>' for s in STATUS_ORDER)
    return (
        "<!doctype html>\n<html lang=\"es\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{escape(title)} · LegacyMapper</title>"
        f'<link rel="stylesheet" href="{root}assets/style.css">{extra_head}</head>\n'
        f'<body data-root="{root}">\n<a class="skip" href="#main">Saltar al contenido</a>\n'
        f'<header class="site"><div class="brand"><a href="{root}index.html">LegacyMapper</a>'
        f'<span>{escape(system_name) if system_name else "Entregables humanos"}</span></div>'
        f'<nav aria-label="Principal"><ul>{nav}</ul></nav>'
        '<div class="search" role="search"><input id="q" type="search" placeholder="Buscar en el paquete…" aria-label="Buscar en el paquete" autocomplete="off">'
        '<ul id="results" hidden></ul></div></header>\n'
        f'<nav class="crumbs" aria-label="Ruta de navegación">{crumb_html}</nav>\n'
        f'<div class="layout">{toc_html}<main id="main">\n{body}\n</main></div>\n'
        f'<footer class="site"><p class="legend-mini"><strong>Estados:</strong> {mini} · '
        f'<a href="{root}about.html">Cómo leer las etiquetas</a></p>'
        '<p class="muted">Paquete estático y portable: funciona desde el disco, sin servidor ni conexión. Generado de forma determinista '
        'a partir de una línea base persistida; no se reanalizó el código fuente ni se invocó a ningún proveedor de IA.</p></footer>\n'
        f'<script src="{root}assets/search-index.js" defer></script><script src="{root}assets/site.js" defer></script>\n'
        "</body></html>\n"
    )


CSS = """\
:root{--bg:#fff;--fg:#111827;--muted:#4b5563;--line:#d1d5db;--soft:#f3f4f6;--link:#1d4ed8;
--confirmed:#1e3a8a;--confirmed-bg:#eef2ff;--inferred:#b45309;--inferred-bg:#fffbeb;--unresolved:#b91c1c;--unresolved-bg:#fef2f2;
--ai:#6d28d9;--ai-bg:#f5f3ff;--canonical:#047857;--canonical-bg:#ecfdf5}
*{box-sizing:border-box}
html{font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;font-size:16px;line-height:1.5;color:var(--fg);background:var(--bg)}
body{margin:0;overflow-wrap:break-word}
main img,main svg,main figure{max-width:100%}
h1,h2,h3,h4,h5,p,li,summary,figcaption,.callout{overflow-wrap:anywhere}   /* flowing text only: last resort after the <wbr> opportunities; tables keep word-level wrapping */
.callout,.card,figure.diagram{max-width:100%}
a{color:var(--link)}
a:focus,summary:focus,input:focus,.table-wrap:focus{outline:3px solid #f59e0b;outline-offset:2px}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:6px;z-index:10}
header.site{display:flex;flex-wrap:wrap;gap:8px 24px;align-items:center;padding:10px 20px;border-bottom:2px solid var(--fg);background:var(--soft)}
.brand a{font-weight:700;font-size:1.15rem;text-decoration:none;color:var(--fg)}.brand span{margin-left:10px;color:var(--muted)}
header nav ul{display:flex;flex-wrap:wrap;gap:4px 14px;list-style:none;margin:0;padding:0}
header nav a{text-decoration:none;padding:2px 6px;border-bottom:3px solid transparent}
header nav a[aria-current]{border-bottom-color:var(--fg);font-weight:700}
.search{position:relative;margin-left:auto}.search input{padding:5px 8px;min-width:220px;border:1px solid var(--line);border-radius:4px}
#results{position:absolute;right:0;top:100%;z-index:5;background:#fff;border:1px solid var(--line);list-style:none;margin:2px 0 0;padding:4px;max-height:50vh;overflow:auto;width:min(480px,90vw)}
#results li a{display:block;padding:4px 6px;text-decoration:none}
.crumbs{padding:8px 20px;font-size:.9rem;color:var(--muted)}
.layout{display:flex;gap:24px;padding:0 20px 40px;align-items:flex-start}
.toc{flex:0 0 240px;position:sticky;top:8px;max-height:90vh;overflow:auto;font-size:.88rem;border:1px solid var(--line);border-radius:6px;padding:8px}
.toc ul{list-style:none;margin:6px 0 0;padding:0}.toc .toc-3{padding-left:14px}.toc li{margin:2px 0}
main{flex:1;min-width:0;max-width:1100px}
h1{font-size:1.7rem;margin:.6em 0 .4em}h2{font-size:1.3rem;margin:0}h3{font-size:1.1rem;margin:1.2em 0 .3em}
details.sec{border-top:1px solid var(--line);padding:8px 0}details.sec>summary{cursor:pointer;list-style-position:outside}
details.sec>summary h2{display:inline}
blockquote{margin:12px 0;padding:6px 14px;border-left:4px solid var(--line);background:var(--soft)}
blockquote p{margin:.4em 0}
.table-wrap{overflow-x:auto;max-width:100%;margin:10px 0}
table{border-collapse:collapse;min-width:50%;font-size:.92rem}
th,td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top;overflow-wrap:break-word;word-break:normal}
th{background:var(--soft)}tbody tr:nth-child(even){background:#fafafa}
code{font-family:ui-monospace,Consolas,"Courier New",monospace;font-size:.88em;background:var(--soft);padding:0 3px;border-radius:3px;overflow-wrap:break-word}
pre{white-space:pre-wrap;overflow-wrap:break-word;max-width:100%;background:var(--soft);padding:8px}
.muted{color:var(--muted);font-size:.9em}
.st{display:inline-block;padding:0 6px;border:2px solid;border-radius:4px;font-size:.85em;font-weight:600;white-space:normal;max-width:100%;overflow-wrap:break-word}
.st-confirmed{color:var(--confirmed);border-color:var(--confirmed);background:var(--confirmed-bg);border-style:solid}
.st-inferred{color:var(--inferred);border-color:var(--inferred);background:var(--inferred-bg);border-style:dashed}
.st-unresolved{color:var(--unresolved);border-color:var(--unresolved);background:var(--unresolved-bg);border-style:dotted}
.st-unresolved::before{content:"! "}
.st-ai{color:var(--ai);border-color:var(--ai);background:var(--ai-bg);border-style:double;border-width:4px}
.st-ai::before{content:"IA · "}
.st-canonical{color:var(--canonical);border-color:var(--canonical);background:var(--canonical-bg);border-style:solid;border-width:4px}
.st-canonical::before{content:"OK · "}
.legend{list-style:none;padding:0}.legend li{margin:6px 0}
.ref-missing{border-bottom:1px dotted var(--muted);cursor:help}
.callout{border:2px solid var(--fg);border-radius:6px;padding:8px 14px;margin:14px 0;background:#fff}
.callout-title{font-weight:700;margin:.2em 0}
.callout-semantic{border-style:dashed;border-color:var(--inferred);background:var(--inferred-bg)}
.callout-unresolved{border-style:dotted;border-color:var(--unresolved);background:var(--unresolved-bg)}
.callout-note{border-color:var(--confirmed);background:var(--confirmed-bg)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:14px;margin:14px 0}
.card{border:1px solid var(--line);border-radius:8px;padding:12px 14px;background:#fff}.card h3{margin-top:0}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(150px,100%),1fr));gap:10px;margin:12px 0}
.kpi div{border:1px solid var(--line);border-radius:6px;padding:8px 10px}.kpi b{display:block;font-size:1.4rem}
figure.diagram{margin:16px 0;padding:10px;border:1px solid var(--line);border-radius:6px;background:#fff}
figure.diagram img{max-width:100%;height:auto;display:block}
figcaption{font-size:.9rem;margin-top:8px}
.tag{display:inline-block;font-size:.75rem;border:1px solid var(--muted);border-radius:3px;padding:0 4px;color:var(--muted)}
.note{font-size:.9rem;color:var(--inferred)}
footer.site{border-top:1px solid var(--line);padding:14px 20px;background:var(--soft);font-size:.9rem}
.filter-box{margin:6px 0}.filter-box input{padding:4px 8px;border:1px solid var(--line);border-radius:4px;min-width:240px}
@media (max-width:900px){.layout{flex-direction:column}.toc{position:static;flex-basis:auto;width:100%}}
@media print{header.site nav,.search,.toc,.skip,footer.site .muted,.filter-box,script{display:none!important}
header.site{border-bottom:1px solid #000;background:#fff}.layout{display:block;padding:0}
html{font-size:11pt}a{color:#000;text-decoration:none}details>summary{list-style:none}
.table-wrap{overflow:visible}table{font-size:9pt}tr,figure{break-inside:avoid}h1,h2,h3{break-after:avoid}
figure.diagram img{max-width:100%}}
"""

JS = """\
(function(){
  'use strict';
  function $(s,r){return (r||document).querySelector(s);}
  // 1. table filter (only for long tables; the table is fully usable without it)
  var wraps=document.querySelectorAll('.table-wrap[data-filter]');
  for(var i=0;i<wraps.length;i++){(function(w){
    var t=w.querySelector('tbody');if(!t)return;
    var box=document.createElement('div');box.className='filter-box';
    var inp=document.createElement('input');inp.type='search';inp.placeholder='Filtrar filas…';inp.setAttribute('aria-label','Filtrar filas de la tabla');
    box.appendChild(inp);w.parentNode.insertBefore(box,w);
    inp.addEventListener('input',function(){
      var q=inp.value.toLowerCase();var rows=t.rows;
      for(var r=0;r<rows.length;r++){rows[r].hidden=q!==''&&rows[r].textContent.toLowerCase().indexOf(q)===-1;}
    });
  })(wraps[i]);}
  // 2. title/heading search over the local index (assets/search-index.js defines LM_SEARCH = [[path,title,headings],...])
  var q=$('#q'),res=$('#results');
  if(!q||!res||typeof LM_SEARCH==='undefined')return;
  var root=document.body.getAttribute('data-root')||'';
  q.addEventListener('input',function(){
    var s=q.value.trim().toLowerCase();res.innerHTML='';
    if(s.length<2){res.hidden=true;return;}
    var n=0;
    for(var i=0;i<LM_SEARCH.length&&n<12;i++){
      var e=LM_SEARCH[i];
      if((e[1]+' '+e[2]).toLowerCase().indexOf(s)!==-1){
        var li=document.createElement('li'),a=document.createElement('a');
        a.href=root+e[0];a.textContent=e[1];li.appendChild(a);res.appendChild(li);n++;
      }
    }
    res.hidden=n===0;
  });
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape'){res.hidden=true;}});
})();
"""
