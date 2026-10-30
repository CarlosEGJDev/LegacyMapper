# AI templates (reserved)

Reserved for future AI prompt/response templates. **Not implemented**: no prompt-template runtime exists yet.

Today the AI contract lives in code (`legacy_documenter/behavior/ai.py`: bounded behavioral context -> structured output schema ->
deterministic validation). The human template system (`templates/human/`) only consumes the *validated* result; it never invokes the AI.
