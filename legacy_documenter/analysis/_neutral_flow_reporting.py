"""Flow/path summary and project-sequence composition helpers for flow resolution (V4.1-R6)."""
from collections import defaultdict


def project_sequence(paths: list[dict]) -> list[str]:
    """Collects first-seen project ids across a set of paths' own project sequences."""
    result = []
    for path in paths:
        for project in path.get("project_sequence", []):
            if project not in result:
                result.append(project)
    return result


def project_sequence_from_nodes(nodes: list[str]) -> list[str]:
    """Derives the first-seen project sequence implied by a path's node ids."""
    result = []
    for item in nodes:
        if "::" not in item:
            continue
        project = item.split("::", 1)[0]
        if project != "<unknown>" and project not in result:
            result.append(project)
    return result


def summary(entries: list[dict], flows: list[dict], paths: list[dict], errors: list[dict]) -> dict:
    """Builds the aggregate resolve() summary dict."""
    terminal_counts = defaultdict(int)
    for path in paths:
        terminal_counts[path["terminal_type"]] += 1
    return {
        "total_entry_points_considered": len([e for e in entries if e.get("confidence") == "confirmed"]),
        "entry_points_with_flows": len(flows),
        "total_flows": len(flows),
        "total_paths": len(paths),
        "paths_to_stored_procedure": terminal_counts["stored_procedure"],
        "paths_to_sql": terminal_counts["sql"],
        "paths_to_data_operation": terminal_counts["data_operation"],
        "unresolved_boundaries": terminal_counts["unresolved_boundary"],
        "external_boundaries": terminal_counts["external_boundary"],
        "dead_end_paths": terminal_counts["dead_end"],
        "cycle_paths": terminal_counts["cycle"],
        "truncated_paths": terminal_counts["truncated_depth"],
        # V4.2-R7.1 F-01: flow-level counterpart to the path-level
        # `unresolved_boundaries` count above -- lets a reader see that a
        # meaningful share of flows with an unresolved boundary path ALSO
        # independently reached a confirmed database terminal, rather than
        # reading `unresolved_boundaries` as "these flows resolved nothing."
        "flows_with_confirmed_terminal": len([f for f in flows if f.get("has_confirmed_terminal")]),
        "flows_with_unresolved_boundary": len([f for f in flows if f.get("has_unresolved_boundary")]),
        "flows_with_both": len([f for f in flows if f.get("has_confirmed_terminal") and f.get("has_unresolved_boundary")]),
        "unique_terminal_stored_procedures": len({p["terminal_target"] for p in paths if p["terminal_type"] == "stored_procedure"}),
        "unique_terminal_sql_operations": len({p["terminal_target"] for p in paths if p["terminal_type"] == "sql"}),
        "cross_project_flows": len([f for f in flows if len(f.get("project_sequence", [])) > 1]),
        "max_observed_depth": max((p["depth"] for p in paths), default=0),
        "average_path_depth": round(sum(p["depth"] for p in paths) / len(paths), 3) if paths else 0,
        "errors": len(errors),
    }
