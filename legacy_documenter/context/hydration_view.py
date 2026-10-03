"""Run-scoped, indexed and memoizing view over one `indexes` dict (V5.3-R2.1).

Kept apart from `hydration.py` (the hydration algorithm itself, unchanged) so that module
does not grow: this one only adds *how the lookups are built once and how results are
shared*. Standard library only; no disk, no global state, nothing persisted.
"""
from copy import deepcopy
from time import perf_counter

from .hydration import EvidenceHydrator, _HydrationLookups


class HydrationView:
    """Run-scoped, indexed and (optionally) memoizing view over one `indexes` dict (V5.3-R2.1).

    One instance is meant to be created per run and passed explicitly to every
    consumer that needs hydrated flows (`consumer_projection`, `HUMAN_DOCUMENTATION`,
    `ai_projection`): the lookups are built once, lazily on first use (so a failure
    to build them surfaces inside the consuming stage's own failure boundary), and
    with `memoize=True` each `flow_id` is hydrated at most once.

    - Bound to the `ix` it was created for: `hydrate_flow(flow_id, ix)` with a
      different `ix` object raises instead of silently mixing evidence.
    - Duck-types `EvidenceHydrator.hydrate_flow(flow_id, ix)`, so it can be passed
      as the `hydrator` of the projection builders.
    - With `memoize=True` the view keeps a pristine record per flow and hands every
      consumer its own deep copy, so no consumer can mutate what another one (or a
      later request) receives. Measured on IST: 12,642 records copy in about 1 s, so
      the defensive copy costs far less than a hydration and is kept.
    - No disk, no global state; nothing here is persisted.
    """

    def __init__(self, ix: dict, hydrator: EvidenceHydrator | None = None, memoize: bool = True) -> None:
        self._ix = ix
        self._hydrator = hydrator or EvidenceHydrator()
        self._memoize = memoize
        self._lookups: _HydrationLookups | None = None
        self._memo: dict[str, dict] = {}
        self.requests = 0
        self.hydrations = 0
        self.memo_hits = 0
        self.build_seconds = 0.0
        self.hydrate_seconds = 0.0

    @property
    def ix(self) -> dict:
        return self._ix

    def hydrate_flow(self, flow_id: str, ix: dict | None = None) -> dict:
        """The hydrated record of `flow_id`; `ix`, if given, must be the dict this view is bound to."""
        if ix is not None and ix is not self._ix:
            raise ValueError("HydrationView is bound to a different indexes dict")
        self.requests += 1
        if self._memoize and flow_id in self._memo:
            self.memo_hits += 1
            return deepcopy(self._memo[flow_id])
        if self._lookups is None:
            started = perf_counter()
            self._lookups = _HydrationLookups(self._ix)
            self.build_seconds = perf_counter() - started
        started = perf_counter()
        record = self._hydrator._hydrate_indexed(flow_id, self._lookups)
        self.hydrate_seconds += perf_counter() - started
        self.hydrations += 1
        if self._memoize:
            self._memo[flow_id] = record
            return deepcopy(record)
        return record

    @property
    def stats(self) -> dict:
        """In-memory characterization counters: hydrations that really ran vs. served from the memo."""
        return {
            "requests": self.requests,
            "hydrations": self.hydrations,
            "memo_hits": self.memo_hits,
            "distinct_flows_hydrated": len(self._memo) if self._memoize else None,
            "build_seconds": round(self.build_seconds, 3),
            "hydrate_seconds": round(self.hydrate_seconds, 3),
        }
