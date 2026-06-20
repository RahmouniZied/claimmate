"""Lexical retrieval over plan clauses. BM25, no external deps."""
import math
import re
from functools import lru_cache
from pathlib import Path

from . import config

_CLAUSE_RE = re.compile(r"^§\s*([0-9]+(?:\.[0-9]+)*)\s+(.*)$")


def parse_clauses(text: str) -> list[dict]:
    """Split a plan document into clauses keyed by id (e.g. 4.2)."""
    clauses: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        m = _CLAUSE_RE.match(line.strip())
        if m:
            if cur:
                clauses.append(cur)
            cur = {"clause_id": m.group(1), "heading": m.group(2).strip(), "text": ""}
        elif cur is not None:
            cur["text"] += line + "\n"
    if cur:
        clauses.append(cur)
    for c in clauses:
        c["text"] = c["text"].strip()
    return clauses


def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())


class PlanIndex:
    def __init__(self, text: str):
        self.clauses = parse_clauses(text)
        self.docs = [_tokens(c["heading"] + " " + c["text"]) for c in self.clauses]
        self.n = len(self.docs)
        self.avgdl = (sum(len(d) for d in self.docs) / self.n) if self.n else 1.0
        self.df: dict[str, int] = {}
        for d in self.docs:
            for t in set(d):
                self.df[t] = self.df.get(t, 0) + 1

    def _idf(self, t: str) -> float:
        n = self.df.get(t, 0)
        return math.log(1 + (self.n - n + 0.5) / (n + 0.5))

    def search(self, query: str, k: int = 5, k1: float = 1.5, b: float = 0.75) -> list[dict]:
        q = _tokens(query)
        scored: list[tuple[float, int]] = []
        for i, d in enumerate(self.docs):
            dl = len(d) or 1
            score = 0.0
            for t in q:
                f = d.count(t)
                if not f:
                    continue
                score += self._idf(t) * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / self.avgdl))
            scored.append((score, i))
        scored.sort(reverse=True)
        out = []
        for score, i in scored[:k]:
            if score <= 0:
                continue
            c = self.clauses[i]
            out.append({"clause_id": c["clause_id"], "heading": c["heading"], "text": c["text"], "score": round(score, 3)})
        return out

    def clause_ids(self) -> set[str]:
        return {c["clause_id"] for c in self.clauses}


@lru_cache(maxsize=8)
def _index_for(path_str: str, mtime: float) -> PlanIndex:
    return PlanIndex(Path(path_str).read_text(encoding="utf-8"))


def active_index() -> PlanIndex:
    """Index for the currently configured plan (cached by path + mtime)."""
    p = Path(config.DEFAULT_PLAN)
    return _index_for(str(p), p.stat().st_mtime)
