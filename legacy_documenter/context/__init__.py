"""Context package creation for later LLM use.

Five modules cooperate here in three stages; none is renamed or moved by this
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
* Hydration stage (V4.3-R2, opt-in, not wired into the CLI pipeline):
  ``hydration.EvidenceHydrator`` takes the same indexes dict
  ``system_context_builder`` consumes and produces one hydrated FLOW record
  per the V4.3-R1 ``AI_HYDRATED_PROJECTION`` contract -- entry point, prioritized
  and deduplicated paths, resolved terminals/parameters, and preserved
  unresolved boundaries, instead of the bare ID references
  ``resolver``/``composer`` produce.
* AI-projection stage (V4.3-R5, opt-in): ``ai_projection.AiProjectionBuilder``
  packages one or more of those hydrated records into an
  ``AI_HYDRATED_PROJECTION 1.0`` envelope (``AIP-`` package id) under a
  **mandatory** budget, reusing ``composer.PROFILES`` but rejecting ``FULL``.
  It is the flow-scoped, bounded input an AI request is built from; it never
  imports ``legacy_documenter.llm`` and never calls a provider. The separate
  limit on the final serialized request payload lives with the request, in
  ``legacy_documenter.llm.core`` and
  ``legacy_documenter.orchestration.ai_interpretation``.
"""
