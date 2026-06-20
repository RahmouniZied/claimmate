"""Deterministic citation gate. Blocks appeals that cite clauses not in the plan."""
import re

_ID_PATTERNS = [
    re.compile(r"§\s*([0-9]+(?:\.[0-9]+)*)"),
    re.compile(r"[Ss]ection\s+([0-9]+(?:\.[0-9]+)*)"),
    re.compile(r"[Cc]lause\s+([0-9]+(?:\.[0-9]+)*)"),
]


def cited_ids(text: str) -> set[str]:
    found: set[str] = set()
    for pat in _ID_PATTERNS:
        found.update(m.group(1) for m in pat.finditer(text or ""))
    return found


def check_citations(appeal_text: str, allowed_ids: set[str]) -> dict:
    """Return cited ids and any that are not present in the plan."""
    cited = cited_ids(appeal_text)
    invalid = sorted(cited - set(allowed_ids))
    return {
        "cited": sorted(cited),
        "invalid": invalid,
        "ok": not invalid,
    }
