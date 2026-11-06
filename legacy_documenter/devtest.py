"""Capability-oriented test runner (dev tooling, stdlib only).

Selects existing ``unittest`` modules from ``tests/`` by capability profile so
day-to-day verification does not require knowing round names::

    python -X utf8 -m legacy_documenter.devtest fast
    python -X utf8 -m legacy_documenter.devtest behavior
    python -X utf8 -m legacy_documenter.devtest packaging
    python -X utf8 -m legacy_documenter.devtest full
    python -X utf8 -m legacy_documenter.devtest list            # profiles and sizes
    python -X utf8 -m legacy_documenter.devtest suggest PATH... # changed path -> profiles
    python -X utf8 -m legacy_documenter.devtest changed         # suggest from `git status`

It never reads a workspace, never calls a provider and never analyses a real
corpus. ``real_ist`` only selects modules; external locations are supplied by
environment variables (see docs/OPERATIONS/TESTING_GUIDE.md).
"""
from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"

# purpose / external dependencies / typical usage / duration class are the
# documented contract of each profile (rendered by `list` and the testing guide).
PROFILE_DOCS: dict[str, dict[str, str]] = {
    "FAST": {
        "purpose": "Smoke check of versions/fingerprints, write-skip and max-path safety, provenance, domain model, exit codes.",
        "external": "none",
        "usage": "after every small edit",
        "duration": "under one minute",
    },
    "CORE": {
        "purpose": "Domain model, contracts, provenance, approval, versions, caches, CLI contract.",
        "external": "none",
        "usage": "shared contract / schema / utils change",
        "duration": "minutes",
    },
    "ANALYSIS": {
        "purpose": "Scanner, adapters, extractors, evidence core, flows, cross-project analysis.",
        "external": "none (synthetic fixtures under tests/fixtures)",
        "usage": "changes under adapters/, extractors/, analysis/, evidence/, scanner/",
        "duration": "minutes",
    },
    "BEHAVIOR": {
        "purpose": "Behavior documentation: screens, actions, wireframes, prototypes, explanations.",
        "external": "none",
        "usage": "changes under behavior/",
        "duration": "minutes",
    },
    "HUMAN_DOCS": {
        "purpose": "Human documentation by audience, templates, readability, layout, evidence separation.",
        "external": "none",
        "usage": "changes under documentation*/, templates/human/",
        "duration": "minutes",
    },
    "AI_KNOWLEDGE": {
        "purpose": "AI interpretation, knowledge model, context budgeting, projections for machines.",
        "external": "none (providers are stubbed)",
        "usage": "changes under llm/, knowledge/, context/, consumers/",
        "duration": "minutes",
    },
    "VISUALS": {
        "purpose": "Structured visual projections (SVG/HTML/PDF).",
        "external": "none",
        "usage": "changes under visuals/",
        "duration": "minutes",
    },
    "PACKAGING": {
        "purpose": "Final per-project package assembly and delivery (human + ai + internal).",
        "external": "none",
        "usage": "changes under deliver/, product/",
        "duration": "minutes",
    },
    "DISTRIBUTION": {
        "purpose": "Wheel/runtime independence, relocation, path portability, plugin/consumer contract.",
        "external": "none",
        "usage": "changes to path utilities, pyproject.toml, packaging",
        "duration": "minutes",
    },
    "PROVIDER": {
        "purpose": "Provider adapters, exit-code contract and the real-provider guard (stubs only).",
        "external": "none (real provider calls stay opt-in and are never made here)",
        "usage": "changes under llm/",
        "duration": "seconds",
    },
    "REAL_IST": {
        "purpose": "Scale / real-corpus regressions. Skips with an explicit reason unless configured.",
        "external": "LEGACYMAPPER_REAL_IST_BASELINE (and LEGACYMAPPER_SOURCE_ROOT for tools)",
        "usage": "milestone validation only, by explicit owner decision",
        "duration": "seconds when skipped; long when configured",
    },
    "FULL": {
        "purpose": "Every test module (release / milestone gate).",
        "external": "none required; external integrations skip with reasons",
        "usage": "milestone closure, release checkpoint, cross-cutting change",
        "duration": "long",
    },
}

# Module-name globs (without the .py suffix). A module may belong to several profiles.
PROFILE_PATTERNS: dict[str, tuple[str, ...]] = {
    "FAST": (
        "test_v5_3_r2_2_write_skip_and_max_path",
        "test_v5_3_r2_3_versioning_and_fingerprints",
        "test_v4_r3_provenance",
        "test_v4_r1_knowledge_domain_model",
        "test_v4_2_r5_1_exit_code_contract_and_real_provider_guard",
    ),
    "CORE": (
        "test_v1*", "test_v3_*", "test_v4_r*", "test_v4_1_r0*", "test_v4_1_r1*", "test_v4_1_r2*", "test_v4_1_r3*",
        "test_v4_1_r4*", "test_v4_1_r7*", "test_v4_2_r1_*", "test_v4_2_r5_*", "test_v4_2_r6_*",
        "test_v5_3_*", "test_post_h5_*",
    ),
    "ANALYSIS": (
        "test_v4_1_r5*", "test_v4_1_r6*", "test_v4_2_r2_*", "test_v4_2_r7_*", "test_v4_2_r8_*",
        "test_v4_3_r2_*", "test_v4_3_r4_*", "test_v5_1_*", "test_v5_4_*", "test_v5_6_*", "test_v5_9_*",
        "test_post_v5_gate_b_*", "test_post_v5_gate_b1_*", "test_post_v5_gate_c_*",
    ),
    "BEHAVIOR": ("test_post_v5_h4_r4_*", "test_post_v5_h4_r5_*"),
    "HUMAN_DOCS": (
        "test_v4_r11_*", "test_v4_2_r3_*", "test_v4_3_r3_human_documentation", "test_v5_2_*", "test_v5_7_*",
        "test_post_v5_h2_*", "test_post_v5_h4_content_polish", "test_post_v5_h4_layout_polish",
        "test_post_v5_h4_noise_pdf_polish", "test_post_v5_h4_screen_narrative",
        "test_post_v5_h4_template_productization", "test_post_v5_h4_evidence_separation",
    ),
    "AI_KNOWLEDGE": (
        "test_v4_2_r4_*", "test_v4_3_r5_*", "test_v4_3_r6_*", "test_v4_3_r3a_*", "test_v4_3_final_ai_*",
        "test_v4_3_r8_*", "test_v5_5_*", "test_post_v5_h1_*", "test_post_v5_h4_knowledge_productization",
    ),
    "VISUALS": ("test_post_v5_h3_*",),
    "PACKAGING": (
        "test_post_v5_h4_deliver", "test_post_v5_h4_template_productization", "test_post_v5_h5_*",
        "test_v4_3_r7_*", "test_v4_r12_*",
    ),
    "DISTRIBUTION": (
        "test_post_v5_gate_a_*", "test_post_v5_gate_a1_*", "test_v4_3_r7_*", "test_v4_r14_*", "test_v5_8_*",
    ),
    "PROVIDER": (
        "test_v4_3_pre_closure_copilot_provider_correction", "test_v4_2_r5_1_*", "test_v5_5_*",
    ),
    "REAL_IST": ("test_post_v5_h5_*", "test_v4_3_r3a_r1_*"),
}

# changed path (repo-relative, forward slashes) -> profiles. First matches all apply.
CHANGED_AREA_MAP: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("legacy_documenter/behavior/*", ("BEHAVIOR",)),
    ("legacy_documenter/visuals/*", ("VISUALS",)),
    ("legacy_documenter/deliver/*", ("PACKAGING",)),
    ("legacy_documenter/product/*", ("PACKAGING", "HUMAN_DOCS")),
    ("legacy_documenter/templates/human/*", ("HUMAN_DOCS", "PACKAGING")),
    ("templates/human/*", ("HUMAN_DOCS", "PACKAGING")),
    ("legacy_documenter/documentation*/*", ("HUMAN_DOCS",)),
    ("legacy_documenter/llm/*", ("PROVIDER", "AI_KNOWLEDGE")),
    ("legacy_documenter/knowledge/*", ("AI_KNOWLEDGE",)),
    ("legacy_documenter/context/*", ("AI_KNOWLEDGE",)),
    ("legacy_documenter/consumers/*", ("AI_KNOWLEDGE", "DISTRIBUTION")),
    ("legacy_documenter/utils/path_*", ("CORE", "DISTRIBUTION")),
    ("legacy_documenter/adapters/*", ("ANALYSIS",)),
    ("adapters/*", ("ANALYSIS",)),
    ("legacy_documenter/extractors/*", ("ANALYSIS",)),
    ("legacy_documenter/scanner/*", ("ANALYSIS",)),
    ("legacy_documenter/analysis/*", ("ANALYSIS",)),
    ("legacy_documenter/evidence/*", ("ANALYSIS", "CORE")),
    ("legacy_documenter/cache/*", ("CORE",)),
    ("legacy_documenter/fingerprints/*", ("CORE",)),
    ("legacy_documenter/cli/*", ("CORE",)),
    ("legacy_documenter/models/*", ("FULL",)),  # shared contract/schema change
    ("legacy_documenter/versions.py", ("FULL",)),
    ("pyproject.toml", ("DISTRIBUTION",)),
    ("tests/*", ("FAST",)),
    ("docs/*", ("FAST",)),
    ("prompts/*", ()),
)


def available_modules() -> list[str]:
    return sorted(p.stem for p in TESTS_DIR.glob("test_*.py"))


def modules_for(profile: str) -> list[str]:
    profile = profile.upper()
    modules = available_modules()
    if profile == "FULL":
        return modules
    patterns = PROFILE_PATTERNS[profile]
    return [m for m in modules if any(fnmatch.fnmatchcase(m, pat) for pat in patterns)]


def unassigned_modules() -> list[str]:
    """Test modules that no capability profile selects (only FULL runs them)."""
    covered = {m for name in PROFILE_PATTERNS for m in modules_for(name)}
    return [m for m in available_modules() if m not in covered]


def profiles_for_paths(paths: list[str]) -> list[str]:
    selected: list[str] = []
    for raw in paths:
        path = raw.replace("\\", "/").lstrip("./")
        for pattern, profiles in CHANGED_AREA_MAP:
            if fnmatch.fnmatchcase(path, pattern):
                for p in profiles:
                    if p not in selected:
                        selected.append(p)
    return selected or ["FAST"]


def run_profile(profile: str, verbosity: int = 1) -> unittest.result.TestResult:
    modules = modules_for(profile)
    sys.path.insert(0, str(REPO_ROOT))
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module in modules:
        suite.addTests(loader.loadTestsFromName(f"tests.{module}"))
    print(f"[devtest] profile={profile.upper()} modules={len(modules)}")
    return unittest.TextTestRunner(verbosity=verbosity).run(suite)


def _git_changed() -> list[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8"
    ).stdout
    return [line[3:].strip().strip('"') for line in out.splitlines() if line[3:].strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="legacy_documenter.devtest", description=__doc__.split("\n")[0])
    parser.add_argument("command", help="profile name, or: list | suggest | changed")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    command = args.command.lower()
    if command == "list":
        for name, doc in PROFILE_DOCS.items():
            print(f"{name:13s} {len(modules_for(name)):4d} modules  [{doc['duration']}]  {doc['purpose']}")
        return 0
    if command == "suggest":
        print(" ".join(profiles_for_paths(args.paths)))
        return 0
    if command == "changed":
        print(" ".join(profiles_for_paths(_git_changed())))
        return 0
    if command.upper() not in PROFILE_DOCS:
        parser.error(f"unknown profile {args.command!r}; use one of {', '.join(n.lower() for n in PROFILE_DOCS)}")
    result = run_profile(command, 2 if args.verbose else 1)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
