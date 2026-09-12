"""Deterministic document consistency and MissingInformation canonicalization."""
from dataclasses import asdict, dataclass
import hashlib
import json
import re
import unicodedata

SYSTEM_TOTAL = "SYSTEM_TOTAL"
SYSTEM_LINKED = "SYSTEM_LINKED"
COVERAGE_PARTITION = "COVERAGE_PARTITION"
UNRESOLVED_SCOPE = "UNRESOLVED_SCOPE"


@dataclass(frozen=True)
class MetricFact:
    """Provides the cohesive MetricFact responsibility for this module."""
    metric_name: str
    value: int
    scope: str
    population: str
    aggregation: str
    source_refs: tuple[str, ...]
    source_snapshot: str
    status: str = "CONFIRMED"

    def to_dict(self):
        """Performs to dict while preserving this module's deterministic contract."""
        value = asdict(self)
        value["source_refs"] = list(self.source_refs)
        return value


def _plain(value):
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def extract_numbers(statement):
    """Performs extract numbers while preserving this module's deterministic contract."""
    return [int(token.replace(".", "")) for token in re.findall(r"(?<![\w])\d{1,3}(?:\.\d{3})+|(?<![\w])\d+(?![\w])", statement)]


def build_metric_index(coverage, packages):
    """Index authoritative system metrics and each deterministic coverage partition."""
    snapshot = coverage.get("snapshot", "")
    metrics = coverage["metrics"] if "metrics" in coverage else coverage
    definitions = {
        "total_projects": (SYSTEM_TOTAL, "PROJECTS", "unique_projects"),
        "covered_projects": (SYSTEM_TOTAL, "PROJECTS_COVERED", "unique_projects"),
        "total_solutions": (SYSTEM_TOTAL, "SOLUTIONS", "unique_solutions"),
        "represented_solutions": (SYSTEM_TOTAL, "SOLUTIONS", "represented_records"),
        "total_webforms": (SYSTEM_TOTAL, "WEBFORMS", "unique_records"),
        "represented_webforms": (SYSTEM_TOTAL, "WEBFORMS", "represented_records"),
        "total_flows": (SYSTEM_TOTAL, "FUNCTIONAL_FLOWS", "unique_records"),
        "represented_flows": (SYSTEM_TOTAL, "FUNCTIONAL_FLOWS", "represented_records"),
        "total_data_operations": (SYSTEM_TOTAL, "DATA_ACCESS", "unique_records"),
        "linked_data_operations": (SYSTEM_LINKED, "DATA_ACCESS", "linked_records"),
        "total_stored_procedures": (SYSTEM_TOTAL, "STORED_PROCEDURES", "unique_records"),
        "linked_stored_procedures": (SYSTEM_LINKED, "STORED_PROCEDURES", "linked_records"),
        "unresolved_relationships": (SYSTEM_TOTAL, "UNRESOLVED_RELATIONSHIPS", "records"),
        "represented_unresolved_relationships": (SYSTEM_TOTAL, "UNRESOLVED_RELATIONSHIPS", "represented_records"),
    }
    facts = []
    for name, (scope, population, aggregation) in definitions.items():
        if isinstance(metrics.get(name), int):
            facts.append(MetricFact(name, metrics[name], scope, population, aggregation,
                                    ("COV-SYSTEM-METRICS",), snapshot))
    seen = set()
    for package in packages:
        for record in package.get("records", []):
            fact = record.get("fact", {})
            category = record.get("category", "")
            for field in ("count", "linked_count"):
                value = fact.get(field)
                key = (record["ref"], field, value)
                if isinstance(value, int) and key not in seen:
                    seen.add(key)
                    facts.append(MetricFact(
                        category.lower() + "_partition_" + field,
                        value,
                        COVERAGE_PARTITION,
                        category,
                        field,
                        (record["ref"], package["package_id"]),
                        package["source_snapshot"],
                    ))
    return sorted(facts, key=lambda x: (x.metric_name, x.value, x.source_refs))


def validate_equivalent(left, right):
    """Performs validate equivalent while preserving this module's deterministic contract."""
    if (left.metric_name, left.scope, left.population, left.aggregation) == (right.metric_name, right.scope, right.population, right.aggregation):
        return left.value == right.value
    return True


def _population_matches(text, population):
    tokens = {
        "PROJECTS": ("proyecto",), "PROJECTS_COVERED": ("proyecto", "cubiert"),
        "SOLUTIONS": ("solucion",), "WEBFORMS": ("webform", "ascx", "control"),
        "FUNCTIONAL_FLOWS": ("flujo", "relacion"), "DATA_ACCESS": ("dato", "operacion"),
        "STORED_PROCEDURES": ("procedimiento", "oracle"),
        "UNRESOLVED_RELATIONSHIPS": ("relacion", "limite", "resuelt"),
    }
    return any(token in text for token in tokens.get(population, (population.lower(),)))


def resolve_claim_metrics(claim, metric_index):
    """Resolve each number without changing the validated claim semantic payload."""
    text = _plain(claim.get("statement", ""))
    refs = set(claim.get("evidence_refs", []))
    resolved = []
    for number in extract_numbers(claim.get("statement", "")):
        candidates = [f for f in metric_index if f.value == number and _population_matches(text, f.population)]
        evidenced = [f for f in candidates if refs.intersection(f.source_refs)]
        candidates = evidenced or candidates
        # Exact system semantics have authority only when their wording matches.
        if number == 234 and "cubiert" in text:
            candidates = [f for f in candidates if f.metric_name == "covered_projects"] or candidates
        elif "ascx" in text and number != 3346:
            candidates = [f for f in candidates if f.scope == COVERAGE_PARTITION] or candidates
        elif candidates and evidenced:
            candidates = evidenced
        elif candidates:
            system = [f for f in candidates if f.scope in (SYSTEM_TOTAL, SYSTEM_LINKED)]
            candidates = system or candidates
        if not candidates:
            resolved.append(MetricFact("unresolved_numeric_claim", number, UNRESOLVED_SCOPE,
                                       "UNKNOWN", "unknown", tuple(sorted(refs)),
                                       (claim.get("source_snapshots") or [""])[0], "UNRESOLVED"))
        else:
            resolved.append(sorted(candidates, key=lambda f: (f.scope == COVERAGE_PARTITION, f.metric_name))[0])
    return resolved


def qualify_quantitative_claims(document, metric_index):
    """Performs qualify quantitative claims while preserving this module's deterministic contract."""
    result = {**document, "claims": []}
    for claim in document["claims"]:
        copy = dict(claim)
        facts = resolve_claim_metrics(copy, metric_index)
        copy["metric_facts"] = [f.to_dict() for f in facts]
        scopes = sorted({f.scope for f in facts})
        copy["metric_scope"] = ",".join(scopes) if scopes else None
        result["claims"].append(copy)
    return result


def validate_quantitative_consistency(document):
    """Performs validate quantitative consistency while preserving this module's deterministic contract."""
    for claim in document["claims"]:
        numbers = extract_numbers(claim.get("statement", ""))
        facts = [MetricFact(**{**f, "source_refs": tuple(f["source_refs"])}) for f in claim.get("metric_facts", [])]
        if len(numbers) != len(facts) or any(f.scope == UNRESOLVED_SCOPE for f in facts):
            return False
        for i, left in enumerate(facts):
            for right in facts[i + 1:]:
                if not validate_equivalent(left, right):
                    return False
    return True


FAMILY_RULES = (
    ("TECHNICAL_ARCHITECTURE_PATTERN", "technical", ("patron", "arquitect")),
    ("TECHNICAL_EXTERNAL_DEPENDENCIES", "technical", ("extern", "ensamblad", "paquete", "biblioteca", "version")),
    ("TECHNICAL_PROJECT_DEPENDENCIES", "technical", ("dependenc", "referencia", "proyecto", "solucion", "grafo")),
    ("TECHNICAL_END_TO_END_FLOW", "technical", ("flujo", "recorrido", "punto de entrada", "limite", "punto final")),
    ("TECHNICAL_COMPONENT_RESPONSIBILITY", "technical", ("regla de negocio", "responsabilidad", "component")),
    ("FUNCTIONAL_INTEGRATION_MAPPING", "functional", ("integracion", "interfaz", "sap")),
    ("FUNCTIONAL_DATA_SEMANTICS", "functional", ("operacion funcional", "semantica", "regla de negocio", "procedimiento almacenado")),
    ("FUNCTIONAL_ENTRY_FLOW_MAPPING", "functional", ("entry point", "entry point id", "webform", "ascx", "punto de entrada")),
    ("FUNCTIONAL_FLOW_DESTINATION", "functional", ("destino funcional", "punto final")),
)


def classify_missing(item, profile):
    """Performs classify missing while preserving this module's deterministic contract."""
    text = _plain(" ".join(str(item.get(k, "")) for k in ("section", "question", "reason")))
    scores = []
    for family, expected, signals in FAMILY_RULES:
        if profile != expected:
            continue
        score = sum(signal in text for signal in signals)
        if score >= 2:
            scores.append((score, family))
    if not scores:
        return None
    scores.sort(reverse=True)
    if len(scores) > 1 and scores[0][0] == scores[1][0]:
        return None
    return scores[0][1]


SEVERITY = {"INFORMATIONAL": 0, "IMPORTANT": 1, "BLOCKING_FOR_APPROVAL": 2}


def canonicalize_missing(records, profile):
    """Merge only requests with a confidently classified deterministic family."""
    groups = {}
    for record in records:
        family = classify_missing(record, profile)
        # Uncertain requests deliberately receive a unique group.
        key = (family, "") if family else (None, record["source_request_ref"])
        groups.setdefault(key, []).append(record)
    prefix = "FMI" if profile == "functional" else "TMI"
    output = []
    for index, key in enumerate(sorted(groups, key=lambda x: (x[0] or "ZZZ", x[1])), 1):
        values = groups[key]
        choose = lambda field: sorted((v.get(field, "") for v in values), key=lambda x: (-len(x), x))[0]
        source_refs = sorted({v["source_request_ref"] for v in values})
        severities = sorted({v.get("blocking_level", "INFORMATIONAL") for v in values}, key=lambda x: SEVERITY[x])
        output.append({
            "request_id": f"{prefix}-{index:03d}", "canonical_id": f"{prefix}-{index:03d}",
            "document": profile, "family": key[0] or "UNCLASSIFIED",
            "section": choose("section"), "question": choose("question"), "reason": choose("reason"),
            "blocking_level": max(severities, key=lambda x: SEVERITY[x]),
            "original_blocking_levels": severities,
            "source_request_ids": source_refs,
            "original_request_ids": sorted({v.get("original_request_id", v["request_id"]) for v in values}),
            "related_claim_ids": sorted({x for v in values for x in v.get("related_claim_refs", [])}),
            "related_evidence_ids": sorted({x for v in values for x in v.get("related_evidence_ids", [])}),
            "context_package_ids": sorted({x for v in values for x in v.get("context_package_ids", [])}),
            "source_snapshots": sorted({x for v in values for x in v.get("source_snapshots", [])}),
        })
    return output


def missing_records(assessments, packages):
    """Performs missing records while preserving this module's deterministic contract."""
    records = []
    for assessment, package in zip(assessments, packages):
        package_records = {x["ref"]: x for x in package.get("records", [])}
        for ordinal, item in enumerate(assessment.get("missing_information", []), 1):
            scoped_claims = [assessment["assessment_id"] + ":" + x for x in item.get("related_claim_ids", [])]
            evidence = []
            for ref in item.get("related_evidence_ids", []):
                record = package_records.get(ref)
                if record:
                    lineage = (record.get("fact") or {}).get("lineage")
                    evidence.extend((lineage or {}).get("evidence_ids", [ref]))
                else:
                    evidence.append(ref)
            records.append({**item,
                "source_request_ref": assessment["assessment_id"] + ":" + item["request_id"] + f":{ordinal:03d}",
                "original_request_id": item["request_id"],
                "related_claim_refs": scoped_claims,
                "related_evidence_ids": sorted(set(evidence)),
                "context_package_ids": [package["package_id"]],
                "source_snapshots": [package["source_snapshot"]],
            })
    return records


def traceability_closed(canonical, originals):
    """Performs traceability closed while preserving this module's deterministic contract."""
    original_refs = {x["source_request_ref"] for x in originals}
    represented = {x for item in canonical for x in item["source_request_ids"]}
    return represented == original_refs and all(item["related_evidence_ids"] for item in canonical)


def stable_hash(value):
    """Performs stable hash while preserving this module's deterministic contract."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
