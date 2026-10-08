"""V5.7 human review: HumanDecision and CanonicalKnowledgeRecord over persisted AI proposals.

Flow: Evidence -> AI Proposal (`proposals/AI_PROPOSALS.json`, read-only here) -> HumanDecision
(`knowledge/decisions/`) -> CanonicalKnowledgeRecord (`knowledge/canonical/`). The AI proposes, a named
human decides, the system validates and persists. Nothing in this package calls a provider, mutates
Evidence or the proposal artifact, or runs unless a human invokes it explicitly.
"""
