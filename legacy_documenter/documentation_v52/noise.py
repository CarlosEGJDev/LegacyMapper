"""Technical Noise Policy (R1 section 8, D-52-03): declarative, technology-agnostic.

The policy is data (`defaults/noise/*.json`, overridable by directory): categories
with a default body visibility, and match rules that assign a candidate to a
category. The *renderer never sees it*; the transformer uses `classify` to tag
items and the profile's `visibility` decides hide/summarize/show.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

VISIBILITIES = ("hide", "summarize", "show")
MATCH_KINDS = ("exact", "prefix", "regex")
MATCH_FIELDS = ("name", "label", "kind")


class NoisePolicyError(ValueError):
    pass


def bare_name(label: str) -> str:
    """Bare callee name of a call expression label: `Me.parametrosURL(  )` -> `parametrosURL`."""
    text = str(label or "").strip()
    text = text.split("(", 1)[0].strip()
    return text.rsplit(".", 1)[-1].strip()


@dataclass
class NoisePolicy:
    id: str
    categories: dict[str, dict]
    rules: list[dict]
    path_markers: list[str] = field(default_factory=list)
    _regex_cache: dict = field(default_factory=dict, repr=False)

    @staticmethod
    def from_dict(data: dict) -> "NoisePolicy":
        if not isinstance(data, dict):
            raise NoisePolicyError("la política de ruido debe ser un objeto JSON")
        for key in ("id", "categories", "patterns"):
            if key not in data:
                raise NoisePolicyError(f"falta el campo '{key}'")
        categories = data["categories"]
        if not isinstance(categories, dict):
            raise NoisePolicyError("'categories' debe ser un objeto")
        for name, spec in categories.items():
            if not isinstance(spec, dict) or spec.get("body_visibility") not in VISIBILITIES:
                raise NoisePolicyError(f"categoría '{name}': body_visibility debe ser una de {VISIBILITIES}")
        rules = data["patterns"]
        if not isinstance(rules, list):
            raise NoisePolicyError("'patterns' debe ser una lista")
        for index, rule in enumerate(rules):
            if rule.get("category") not in categories:
                raise NoisePolicyError(f"patrón #{index}: categoría desconocida {rule.get('category')!r}")
            if rule.get("on") not in MATCH_FIELDS or rule.get("match") not in MATCH_KINDS:
                raise NoisePolicyError(f"patrón #{index}: 'on'/'match' inválidos")
            if not isinstance(rule.get("values"), list) or not rule["values"]:
                raise NoisePolicyError(f"patrón #{index}: 'values' debe ser una lista no vacía")
            if rule["match"] == "regex":
                for value in rule["values"]:
                    try:
                        re.compile(value)
                    except re.error as exc:
                        raise NoisePolicyError(f"patrón #{index}: expresión inválida {value!r}: {exc}") from exc
        return NoisePolicy(
            id=str(data["id"]), categories=dict(categories), rules=list(rules),
            path_markers=[str(item) for item in data.get("path_markers", [])],
        )

    def classify(self, *, name: str = "", label: str = "", kind: str = "") -> str | None:
        """First matching category (rules are ordered) or `None`."""
        fields = {"name": name, "label": label, "kind": kind}
        for rule in self.rules:
            candidate = fields[rule["on"]]
            if not candidate:
                continue
            lowered = candidate.lower()
            for value in rule["values"]:
                if rule["match"] == "exact":
                    hit = lowered == value.lower()
                elif rule["match"] == "prefix":
                    hit = lowered.startswith(value.lower())
                else:
                    pattern = self._regex_cache.get(value)
                    if pattern is None:
                        pattern = self._regex_cache[value] = re.compile(value, re.IGNORECASE)
                    hit = pattern.search(candidate) is not None
                if hit:
                    return rule["category"]
        return None

    def visibility(self, category: str, overrides: dict | None = None) -> str:
        if overrides and category in overrides:
            return overrides[category]
        return self.categories[category]["body_visibility"]

    def counts_as_data_access(self, category: str | None) -> bool:
        """`False` for infrastructure categories declared `"counts_as_data_access": false`
        (e.g. transaction control): they are not a real query/procedure."""
        return category is None or self.categories[category].get("counts_as_data_access", True)

    def dependency_class(self, category: str | None) -> str | None:
        """Optional `"dependency_class"` a category declares (e.g. `platform`)."""
        return None if category is None else self.categories[category].get("dependency_class")

    def path_marker(self, path: str) -> str | None:
        lowered = str(path).lower()
        for marker in self.path_markers:
            if marker.lower() in lowered:
                return marker
        return None
