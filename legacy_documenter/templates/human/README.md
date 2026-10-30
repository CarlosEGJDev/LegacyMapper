# Human templates (LegacyMapperHumanTemplate 1.0)

A human template controls **layout and presentation** of the behavioral documentation. It never changes truth.

```text
legacy_documenter/templates/human/<name>/
├── template.yaml   contract, id/version, audience, language, section order, chapter parts, required/optional fields, labels
├── document.html   HTML shell with a closed set of {{placeholders}}
├── styles.css      HTML presentation (typography hierarchy, badges, callouts)
├── pdf.css         PDF presentation (font-size / colour of .doc-title .h1 .h2 .h3 .body .caption .technical .evidence .badge)
└── assets/         optional plain files listed under `assets:`
```

Rules enforced by `legacy_documenter.behavior.template`:

* Placeholders: `title subtitle lang style toc ai_notice content legend footer script template_id template_version` (no expressions, loops or includes).
* `document.html` cannot contain scripts, event handlers, frames or `meta http-equiv`; CSS cannot use `@import`, `url()`, expressions or scripts.
* Required sections: `cover ai_notice toc solution project view_chapters unresolved appendix`. Required chapter parts: `title one_line what_it_does usage flow actions` (a template can never hide `UNRESOLVED`: the unresolved section and the flow/actions parts are mandatory).
* A template receives the already validated model: it cannot promote `AI_INTERPRETATION`, hide `UNRESOLVED`, edit `source_refs`, mutate the baseline or call a provider.

Use a template: `python -m legacy_documenter.behavior.prototype <baseline> --output <dir> --template human/default [--template-dir <dir>]`.
The built-in templates live inside the package (`legacy_documenter/templates/`) and travel with it; a user directory (`--template-dir`) is searched before them and never mutates them.

Built-in templates: `human/default` (full guide) and `human/executive` (executive reading order: solution -> project -> capabilities -> data impact -> unresolved -> minimal chapters; same model, same claims, same statuses and references).
