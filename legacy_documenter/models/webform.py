from dataclasses import dataclass, field, asdict


@dataclass
class WebForm:
    """Provides the cohesive WebForm responsibility for this module."""
    path: str
    kind: str
    directives: list[dict] = field(default_factory=list)
    codebehind: str | None = None
    codefile: str | None = None
    inherits: str | None = None
    master_page: str | None = None
    registers: list[dict] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    stylesheets: list[str] = field(default_factory=list)
    markup_events: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Performs to dict while preserving this module's deterministic contract."""
        return asdict(self)
