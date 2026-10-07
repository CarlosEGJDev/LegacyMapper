"""String-literal and token parsing helpers for VB.NET expression scanning (V4.1-R6)."""
import re

SQL_RE = re.compile(r"^\s*(SELECT|INSERT|UPDATE|DELETE|MERGE)\b", re.IGNORECASE)


def strip_string_literals(line: str) -> str:
    """Blanks out quoted string contents so later regexes ignore text inside them."""
    result = []
    in_string = False
    idx = 0
    while idx < len(line):
        if line[idx] == '"':
            in_string = not in_string
            result.append(" ")
        elif in_string:
            result.append(" ")
        else:
            result.append(line[idx])
        idx += 1
    return "".join(result)


def literal(expr: str | None) -> str | None:
    """Extracts a VB string-literal's value, unescaping doubled quotes."""
    if not expr:
        return None
    match = re.match(r'^\s*"(?P<value>(?:""|[^"])*)"\s*$', expr.strip())
    return match.group("value").replace('""', '"') if match else None


def sql_kind(text: str | None) -> str | None:
    """Classifies leading SQL keyword text, if any."""
    if not text:
        return None
    match = SQL_RE.match(text)
    return match.group(1).upper() if match else None


def first_sql_keyword(expr: str) -> str | None:
    """Finds the first quoted SQL keyword in a dynamic-SQL expression."""
    match = re.search(r'"(?:\s*)(SELECT|INSERT|UPDATE|DELETE|MERGE)\b', expr, re.IGNORECASE)
    return match.group(1).upper() if match else None


def split_args(args: str) -> list[str]:
    """Splits a call's argument text on top-level commas, respecting quotes/parens."""
    parts = []
    current = []
    depth = 0
    in_string = False
    idx = 0
    while idx < len(args):
        char = args[idx]
        if char == '"':
            in_string = not in_string
        elif not in_string:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif char == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
                idx += 1
                continue
        current.append(char)
        idx += 1
    if current or args.strip():
        parts.append("".join(current).strip())
    return parts
