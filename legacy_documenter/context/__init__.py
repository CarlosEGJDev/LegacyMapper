"""Context package creation for later LLM use.

Four modules cooperate here in two stages; none is renamed or moved by this
docstring, which only records how they relate for a reader unfamiliar with
the package:

* Write stage (invoked once per repository scan, from ``legacy_documenter.main.analyze_repository``):
  ``context_builder.ContextBuilder`` writes ``output/context/projects.json``
  (a per-project technology/dependency summary) and
  ``system_context_builder.SystemContextBuilder`` writes the
  ``output/ai_context/*.json`` artifacts (``SYSTEM_CONTEXT.json``,
  ``FUNCTIONAL_FLOWS.json``, ``TRACEABILITY.json``) that the read stage
  below consumes.
* Read stage (invoked later, from the V3 documentation generators):
  ``resolver.ContextResolver`` loads those same ``ai_context/*.json``
  artifacts and resolves/looks up flows, paths, and entry points by id;
  ``composer.ContextComposer`` wraps a ``ContextResolver`` to apply a
  token/record budget and produce one bounded, truncation-aware context
  package for a single LLM request.
"""
