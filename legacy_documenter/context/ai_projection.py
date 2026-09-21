"""Budgeted `AI_HYDRATED_PROJECTION 1.0` package construction (V4.3-R5).

Implements the `ai_projection` surface fixed by V4.3-R1 section 5.2
(`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`): a package whose
`records` are **hydrated FLOW records** (produced by
`legacy_documenter.context.hydration.EvidenceHydrator.hydrate_flow`, V4.3-R2 --
never re-implemented here), carried inside the same envelope shape
`legacy_documenter.context.composer.ContextComposer` already produces
(`package_type`/`schema_version`/`package_id`/`source_snapshot`/`statistics`/
`truncation`), with `AIP-` as the package-id prefix instead of `CTX-`.

Why this module exists (V4.3-R0 defect `D-01`, external finding `EEE-02`): a
`SYSTEM` context package with no mandatory ceiling produced a ~13.8 MB /
~3.6 M token real prompt. Three rules, all enforced here, close that hole:

1. **The budget is mandatory, not optional.** A package is always built for an
   explicit, bounded list of `flow_id`s (`build_ai_projection` refuses `None`)
   and always under one of the existing `TINY`/`SMALL`/`MEDIUM`/`LARGE`
   profiles reused verbatim from `composer.PROFILES` -- never reinvented here.
2. **`FULL` is not a valid profile for this surface.** `composer.PROFILES`
   still offers it (`10**9` records/characters) for the pre-existing reference
   packages, but R1 section 5.2 states "un paquete `ai_projection` sin techo de
   presupuesto no es conforme a este contrato"; asking for it raises
   `ValueError` (see `ALLOWED_PROFILES`).
3. **This package's own budget never authorizes a provider call.** It bounds
   `records` only. The final serialized `LLMRequest` payload (system/user
   instruction, output schema, envelope, records, statistics, truncation) is
   measured and gated separately -- see
   `legacy_documenter.llm.core.measure_request_payload` and
   `legacy_documenter.orchestration.ai_interpretation`'s gate. R1 section 5.2
   is explicit that satisfying this module's budget alone is not sufficient.

Like `hydration.py`, this module is a pure function of the `ix` indexes dict
and the hydrated records derived from it: it never imports
`legacy_documenter.llm`, never calls a provider, never reads or writes a file,
and never mutates or invents a `confidence` value on any hydrated record. The
`AI_HYDRATED_PROJECTION 1.0` contract additionally forbids carrying
`INTERPRETED`/AI-produced content as *input* evidence (R1 section 5.2); that is
enforced structurally by `_reject_interpreted_content`, not merely documented.
"""
import hashlib
import json
import math

from .composer import PROFILES
from .hydration import CONFIDENCE_ORDER, MODEL_VERSION as HYDRATION_MODEL_VERSION, EvidenceHydrator

CONTRACT_NAME = "AI_HYDRATED_PROJECTION"
CONTRACT_VERSION = "1.0"
SCHEMA_VERSION = "1.0"
PACKAGE_TYPE = "AI_PROJECTION"

#: Same computation as `ContextComposer.compose`'s `package_id` (canonical
#: SHA-256 over the serialized body), with the R1 section 4 prefix for this
#: surface (`AIP-`) instead of `CTX-`.
PACKAGE_ID_PREFIX = "AIP-"

#: The profiles a `ai_projection` package may be built with -- the same four
#: entries `composer.PROFILES` already defines, minus `FULL`. `FULL` is
#: `(10**9, 10**9)`, i.e. effectively unbounded, which is exactly the D-01
#: defect this surface exists to close; it is rejected rather than silently
#: clamped so a caller can never believe it got an unbounded package.
ALLOWED_PROFILES = ("TINY", "SMALL", "MEDIUM", "LARGE")

#: Ordered reduction ladder used by a caller that wants to retry with a
#: smaller package after a payload-size gate rejected the first attempt
#: (`legacy_documenter.orchestration.ai_interpretation`). Exposed here so the
#: ladder is defined once, next to the profiles it reduces between.
PROFILE_REDUCTION = {"LARGE": "MEDIUM", "MEDIUM": "SMALL", "SMALL": "TINY"}

#: Tokens that would indicate AI-produced interpretation being smuggled in as
#: deterministic input evidence. R1 section 5.2: a package on this surface
#: carries "exclusivamente evidencia determinista hidratada
#: (`CONFIRMED`/`UNRESOLVED`)" and "no incluye resultados
#: `INTERPRETED`/`AI_INTERPRETATION` de ejecuciones de IA anteriores".
FORBIDDEN_CONTENT_TOKENS = ("interpreted", "ai_interpretation", "interpretations")


class InterpretedContentError(ValueError):
    """Raised when a record offered for projection carries AI-interpreted content.

    This is a contract violation by the caller, not a report of missing
    evidence: `AI_HYDRATED_PROJECTION 1.0` is the *input* sent to a provider,
    never an accumulator of a previous run's interpretations (R1 section 5.2,
    "no mecanismo de interpretación recursiva").
    """


#: Raw SQL verbs `DatabaseExtractor` already records on a data-access operation's
#: own `sql_operation` field (V4.3-R3) that represent a write, as opposed to a
#: read (`SELECT`). Reused only to classify already-extracted evidence -- never
#: to infer a write from a stored procedure's name (V4.3-R3, R0 acceptance C).
_WRITE_OPERATIONS = frozenset({"INSERT", "UPDATE", "DELETE", "MERGE"})


def _richness_bucket(has_resolved_terminal: bool, has_confirmed_data_operation: bool, has_secondary_diversity: bool) -> int:
    """Ranks a flow/record from richest (0) to trivial (3) using only already-computed evidence.

    Orthogonal to `CONFIDENCE_ORDER`: this never reads or reorders by a flow's own
    `confidence` label, and it is only ever used as a *secondary* diversity key
    -- the V4.3 final AI pilot found that `PROPOSAL_GENERATION`'s limited slots
    were consumed almost entirely by flows whose statement is "has no recorded
    data operations and ends at an unresolved node", even though flows with
    confirmed stored procedures, SQL terminals, transactions or write evidence
    existed in the same repository. Bucket 0 covers a resolved (non-`unresolved_
    boundary`) terminal or a confirmed write/transaction; bucket 1 covers any
    other confirmed data operation; bucket 2 covers flows offering some other
    diversity signal (mixed confirmed/unresolved paths, multiple participating
    components, or multiple evidence references) even without a resolved
    terminal; bucket 3 is exactly the homogeneous "no recorded data operations,
    unresolved terminal" case the pilot over-selected.
    """
    if has_resolved_terminal:
        return 0
    if has_confirmed_data_operation:
        return 1
    if has_secondary_diversity:
        return 2
    return 3


def _bucketed_order(items: list, bucket_of, tiebreak_key) -> list:
    """Reorders `items` round-robin across richness buckets 0 (richest) to 3 (trivial).

    Deterministic and stable: each bucket is internally sorted by `tiebreak_key`
    first, then one item is drawn from each non-empty bucket in turn (0, 1, 2, 3)
    until every item has been placed. This is how a small, budget-limited
    selection avoids being exhausted entirely by the trivial bucket when richer
    candidates exist elsewhere, while degrading safely (using only what is
    available) when they do not. No randomness, no LLM involvement, no mutation
    of any item.
    """
    buckets: dict[int, list] = {0: [], 1: [], 2: [], 3: []}
    for item in items:
        buckets[bucket_of(item)].append(item)
    for bucket in buckets.values():
        bucket.sort(key=tiebreak_key)
    ordered: list = []
    cursors = {key: 0 for key in buckets}
    while len(ordered) < len(items):
        progressed = False
        for key in (0, 1, 2, 3):
            if cursors[key] < len(buckets[key]):
                ordered.append(buckets[key][cursors[key]])
                cursors[key] += 1
                progressed = True
        if not progressed:
            break
    return ordered


def _flow_richness_bucket(flow: dict, paths_by_flow: dict, data_access: dict) -> int:
    """Pre-hydration proxy richness bucket for a raw `functional_flows` entry.

    Reads only fields `hydration.EvidenceHydrator` itself already reads off
    `ix` (a path's own `terminal_type`/`nodes`/`terminal_target`/`confidence`/
    `evidence_refs`, and a data-access record's own `sql_operation`/
    `operation_kind`/`confidence`) -- it never re-derives evidence, never calls
    the hydrator, and never mutates anything. Computed pre-hydration (cheaply,
    from indexes already in memory) so the flow *selection* step itself -- not
    only the later character-budget packing -- stops letting trivial flows
    crowd out richer ones before richer ones are even hydrated.
    """
    paths = paths_by_flow.get(flow.get("id"), [])
    has_resolved_terminal = any(p.get("terminal_type") in ("stored_procedure", "sql") for p in paths)
    has_confirmed_data_operation = False
    for path in paths:
        node_ids = list(path.get("nodes", []))
        if path.get("terminal_target") is not None:
            node_ids.append(path["terminal_target"])
        for node_id in node_ids:
            record = data_access.get(node_id)
            if record is None or record.get("confidence") != "confirmed":
                continue
            if record.get("sql_operation") is not None or record.get("operation_kind") == "transaction":
                has_confirmed_data_operation = True
    path_confidences = {p.get("confidence") for p in paths}
    has_mixed_evidence = "unresolved" in path_confidences and bool(path_confidences - {"unresolved"})
    multiple_components = len(set(flow.get("project_sequence", []))) > 1
    multiple_evidence_refs = sum(len(p.get("evidence_refs", []) or []) for p in paths) > 1
    return _richness_bucket(
        has_resolved_terminal, has_confirmed_data_operation,
        has_mixed_evidence or multiple_components or multiple_evidence_refs,
    )


def select_flow_ids(ix: dict, max_flows: int) -> list[str]:
    """Deterministically selects at most `max_flows` flow ids from `ix`.

    "Prefer FLOW and controlled aggregations" (the R5 prompt) means a caller
    that does not name its own flows still never gets an unbounded `SYSTEM`
    sweep: `max_flows` is mandatory and must be positive. Within each richness
    bucket (`_flow_richness_bucket`), order is still confirmed-before-inferred-
    before-unresolved, then `flow_id` ascending -- the same priority policy
    `hydration.select_and_deduplicate_paths` already applies to paths, reused
    rather than reinvented. Across buckets, `_bucketed_order` round-robins so a
    small `max_flows` is not exhausted entirely by flows with no resolved
    terminal and no data operations when richer candidates exist (V4.3 final AI
    pilot proposal quality correction).
    """
    if not isinstance(max_flows, int) or max_flows <= 0:
        raise ValueError("max_flows must be a positive integer")
    flows = [f for f in ix.get("functional_flows", []) if f.get("id")]
    paths_by_flow: dict = {}
    for path in ix.get("functional_paths", []):
        paths_by_flow.setdefault(path.get("flow_id"), []).append(path)
    data_access = {d["id"]: d for d in ix.get("data_access", []) if d.get("id")}
    ordered = _bucketed_order(
        flows,
        bucket_of=lambda f: _flow_richness_bucket(f, paths_by_flow, data_access),
        tiebreak_key=lambda f: (CONFIDENCE_ORDER.get(f.get("confidence"), 99), f["id"]),
    )
    return [f["id"] for f in ordered[:max_flows]]


def record_reference_ids(record: dict) -> set:
    """Every deterministic id a hydrated FLOW record makes citable.

    This is the closed set an AI answer's `evidence_refs` may cite (see
    `legacy_documenter.orchestration.ai_interpretation._validate_findings`): the
    flow itself, its entry point, each merged `path_id`, every node/terminal id
    reached, and every `evidence_refs` entry already recorded on each path.
    Nothing is invented here -- every value is read verbatim off the record.
    """
    refs: set = set()
    for value in (record.get("flow_id"), (record.get("entry_point") or {}).get("id")):
        if value:
            refs.add(value)
    for path in record.get("paths", []):
        refs.update(pid for pid in path.get("path_ids", []) if pid)
        refs.update(ref for ref in path.get("evidence_refs", []) if ref)
        for node in path.get("nodes", []):
            if node.get("id"):
                refs.add(node["id"])
        terminal_id = (path.get("terminal") or {}).get("id")
        if terminal_id:
            refs.add(terminal_id)
    return refs


def package_reference_ids(package: dict) -> set:
    """Union of `record_reference_ids` over every record actually included.

    Deliberately computed over `package["records"]` only -- never over records
    a budget excluded -- so a model can only cite evidence it was actually
    shown.
    """
    refs: set = set()
    for record in package.get("records", []):
        refs |= record_reference_ids(record)
    return refs


def _reject_interpreted_content(record: dict) -> None:
    """Fails closed if `record` carries AI-interpreted content anywhere inside it."""
    text = _canonical(record).lower()
    for token in FORBIDDEN_CONTENT_TOKENS:
        # The quoted form matches the token as a key or as a value, and never
        # as a substring of an unrelated identifier.
        if f'"{token}"' in text:
            raise InterpretedContentError(token)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _record_richness_bucket(record: dict) -> int:
    """Post-hydration richness bucket for one hydrated FLOW record.

    Reads only fields `hydration.EvidenceHydrator.hydrate_flow` already
    computed (`terminals`, `data_operations`, `transactions`, `paths`,
    `projects`) -- never re-derives evidence and never mutates the record.
    Mirrors `_flow_richness_bucket`'s pre-hydration proxy but uses the exact
    hydrated evidence now available, since this is the pass that decides which
    records survive the character-budget truncation in `AiProjectionBuilder
    .package`.
    """
    terminals = record.get("terminals") or {}
    has_resolved_terminal = bool(terminals.get("stored_procedures")) or bool(terminals.get("sql_operations"))
    has_confirmed_write = any(
        op.get("operation") in _WRITE_OPERATIONS and op.get("confidence") == "confirmed"
        for op in record.get("data_operations", [])
    )
    has_confirmed_transaction = any(tx.get("confidence") == "confirmed" for tx in record.get("transactions", []))
    has_confirmed_data_operation = any(
        op.get("confidence") == "confirmed" for op in record.get("data_operations", [])
    )
    paths = record.get("paths", [])
    path_confidences = {p.get("confidence") for p in paths}
    has_mixed_evidence = "unresolved" in path_confidences and bool(path_confidences - {"unresolved"})
    multiple_components = len(set(record.get("projects", []))) > 1
    multiple_evidence_refs = sum(len(p.get("evidence_refs", []) or []) for p in paths) > 1
    return _richness_bucket(
        has_resolved_terminal or has_confirmed_write or has_confirmed_transaction,
        has_confirmed_data_operation,
        has_mixed_evidence or multiple_components or multiple_evidence_refs,
    )


class AiProjectionBuilder:
    """Builds one budgeted `AI_HYDRATED_PROJECTION 1.0` package from hydrated FLOW records."""

    CONTRACT_NAME = CONTRACT_NAME
    CONTRACT_VERSION = CONTRACT_VERSION

    def __init__(self, hydrator: object = None, chars_per_token: int = 4) -> None:
        self.hydrator = hydrator or EvidenceHydrator()
        self.chars_per_token = chars_per_token

    def build(
        self, flow_ids: list[str], ix: dict, source_snapshot: str | None = None,
        profile: str = "SMALL", budget: dict | None = None,
    ) -> dict:
        """Hydrates `flow_ids` and packages them under a mandatory budget.

        `flow_ids` must be an explicit, bounded list -- `None` is rejected
        rather than interpreted as "every flow" (D-01). `profile` must be one
        of `ALLOWED_PROFILES`; `FULL` raises `ValueError`. `budget` may only
        tighten the profile, exactly as `ContextComposer.compose` already
        allows (`max_records`/`max_characters`/`max_estimated_tokens`).
        """
        if flow_ids is None:
            raise ValueError("flow_ids is mandatory: an ai_projection package is never an unbounded sweep")
        if profile == "FULL":
            raise ValueError("profile FULL is not valid for ai_projection (AI_HYDRATED_PROJECTION 1.0 requires a ceiling)")
        if profile not in ALLOWED_PROFILES:
            raise ValueError("profile")
        records = [self.hydrator.hydrate_flow(flow_id, ix) for flow_id in sorted(set(flow_ids))]
        return self.package(records, source_snapshot=source_snapshot, profile=profile, budget=budget)

    def package(
        self, records: list[dict], source_snapshot: str | None = None,
        profile: str = "SMALL", budget: dict | None = None,
    ) -> dict:
        """Packages already-hydrated records under the same budget rules as `build`."""
        if profile == "FULL":
            raise ValueError("profile FULL is not valid for ai_projection (AI_HYDRATED_PROJECTION 1.0 requires a ceiling)")
        if profile not in ALLOWED_PROFILES:
            raise ValueError("profile")
        for record in records:
            _reject_interpreted_content(record)
        budget = budget or {}
        max_records, max_chars = PROFILES[profile]
        max_records = budget.get("max_records", max_records)
        max_chars = min(
            budget.get("max_characters", max_chars),
            budget.get("max_estimated_tokens", 10 ** 18) * self.chars_per_token,
        )

        ordered = _bucketed_order(
            records,
            bucket_of=_record_richness_bucket,
            tiebreak_key=lambda r: (CONFIDENCE_ORDER.get(r.get("confidence"), 99), str(r.get("flow_id"))),
        )
        capped = ordered[: max(max_records, 0)]

        # Exact character accounting without re-serializing the whole body once
        # per candidate record: a canonical JSON list of n items costs
        # `2 + sum(len(item_i)) + (n - 1)` characters, so the envelope's own
        # cost (measured with `records: []`) plus those terms is the exact
        # length of the final canonical body. This total is order-independent
        # (only the *set* and *count* of chosen records matter, never the
        # sequence they are accepted in), which is what makes the two-pass
        # reservation below safe: reserving a record out of its natural
        # `capped` position never changes the final character total.
        envelope_chars = len(_canonical(self._body(profile, budget, source_snapshot, [])))
        costs = [len(_canonical(record)) for record in capped]

        accepted = [False] * len(capped)
        used = 0
        count = 0

        def _try_accept(index: int) -> bool:
            nonlocal used, count
            extra = costs[index] + (1 if count else 0)
            if envelope_chars + used + extra > max_chars:
                return False
            accepted[index] = True
            used += extra
            count += 1
            return True

        # Reservation pass (V4.3-R3A-R1, layer-2 fix): `_bucketed_order`'s own
        # round-robin/confidence/flow_id order still decides evaluation order,
        # but a strict first-fit-greedy single pass over that order lets small
        # bucket-2/3 (trivial) records -- which appear early in every
        # round-robin cycle -- exhaust the budget before the packer ever
        # reaches a bucket-0/1 (rich) candidate of reasonable size, even when
        # that rich candidate individually fits the complete budget (the
        # demonstrated real case: 5 of 40 rich candidates fit individually,
        # 0 survived). Guarantee, before any other acceptance happens, the
        # first bucket-0 candidate that individually fits and then the first
        # bucket-1 candidate that individually fits (in the same
        # confidence/flow_id order `_bucketed_order` already established for
        # each bucket) -- never more than one per bucket, so this cannot
        # revert to rich records monopolizing the sample (diversity
        # invariant). If no candidate in a bucket fits at all (layer-1
        # outliers), nothing is reserved for it and the backfill pass below
        # behaves exactly as before.
        for bucket_wanted in (0, 1):
            for index, record in enumerate(capped):
                if accepted[index] or _record_richness_bucket(record) != bucket_wanted:
                    continue
                if _try_accept(index):
                    break

        # Backfill pass: the same first-fit-greedy as before V4.3-R3A-R1,
        # over whatever budget the reservation pass above left, in the exact
        # same `capped` order -- never `break` on the first oversized
        # candidate (V4.3 final AI pilot R2: that let one large,
        # richness-prioritized record block every smaller candidate after it).
        for index in range(len(capped)):
            if accepted[index]:
                continue
            _try_accept(index)

        # The final `records` list keeps `capped`'s own bucket/confidence/
        # flow_id order regardless of which pass accepted each item, so a
        # reserved rich record appears at its natural position rather than
        # being pulled to the front.
        chosen = [record for index, record in enumerate(capped) if accepted[index]]

        excluded = len(ordered) - len(chosen)
        minimum_chars = envelope_chars + (min(costs) if costs else 0)
        insufficient = bool(capped) and not chosen
        completeness = "BUDGET_INSUFFICIENT" if insufficient else ("TRUNCATED" if excluded else "COMPLETE")

        body = self._body(profile, budget, source_snapshot, chosen)
        text = _canonical(body)
        body["statistics"] = {
            "package_bytes": len(text.encode()),
            "character_count": len(text),
            "estimated_tokens": math.ceil(len(text) / self.chars_per_token),
            "estimation_method": "approximation: ceil(chars/chars_per_token)",
            "chars_per_token": self.chars_per_token,
            "records_selected": len(ordered),
            "records_included": len(chosen),
            "records_excluded": excluded,
            "flow_count": len(chosen),
            "path_count": sum(len(r.get("paths", [])) for r in chosen),
            "confirmed_flow_count": sum(r.get("confidence") == "confirmed" for r in chosen),
            "inferred_flow_count": sum(r.get("confidence") == "inferred" for r in chosen),
            "unresolved_flow_count": sum(r.get("confidence") == "unresolved" for r in chosen),
            "max_records": max_records,
            "max_characters": max_chars,
            "minimum_required_characters": minimum_chars,
            "budget_profile": profile,
            "completeness": completeness,
        }
        # Deliberately **counts only**: the excluded flow ids are never carried
        # as a `continuation_refs` list the way `ContextComposer` does. On a
        # real repository that list is unbounded and is exactly the kind of
        # bulk metadata the R5 prompt forbids sending ("no enviar metadata/
        # continuations masivas innecesarias"); a caller that wants the
        # excluded flows asks for them as their own bounded package.
        body["truncation"] = {
            "truncated": completeness != "COMPLETE",
            "excluded_record_count": excluded,
            "continuation_refs_included": False,
            "continuation_policy": "EXCLUDED_FLOWS_ARE_REQUESTED_AS_SEPARATE_BOUNDED_PACKAGES",
        }
        body["package_id"] = PACKAGE_ID_PREFIX + hashlib.sha256(_canonical(body).encode()).hexdigest()
        return body

    def _body(self, profile: str, budget: dict, source_snapshot: str | None, records: list[dict]) -> dict:
        return {
            "package_type": PACKAGE_TYPE,
            "contract_name": CONTRACT_NAME,
            "contract_version": CONTRACT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "source_snapshot": source_snapshot,
            "scope": {"flow_ids": [r.get("flow_id") for r in records]},
            "selection_policy": {
                "surface": "ai_projection",
                "budget_profile": profile,
                "budget": budget,
                "priority_policy": "confirmed_before_inferred_before_unresolved",
                "full_profile_allowed": False,
            },
            "records": records,
            "provenance": {
                "hydration_model_version": HYDRATION_MODEL_VERSION,
                "source_indexes": [
                    "index/functional_flows.json", "index/functional_paths.json", "index/entry_points.json",
                    "index/data_access.json", "index/stored_procedures.json", "index/sql_operations.json",
                    "index/data_parameters.json",
                ],
            },
        }


def build_ai_projection(
    flow_ids: list[str], ix: dict, source_snapshot: str | None = None,
    profile: str = "SMALL", budget: dict | None = None, chars_per_token: int = 4,
) -> dict:
    """Module-level convenience wrapper over `AiProjectionBuilder.build`."""
    return AiProjectionBuilder(chars_per_token=chars_per_token).build(
        flow_ids, ix, source_snapshot=source_snapshot, profile=profile, budget=budget,
    )
