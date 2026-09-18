"""Controlled, relationship-backed TargetPair search and submission validation."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable


@dataclass(frozen=True)
class TargetPairOption:
    name: str
    targets: tuple[str, ...]


def fetch_target_pairs(runner: Any) -> list[TargetPairOption]:
    # Only this small catalogue bypasses the general report row limit.
    rows = runner.run(
        """
MATCH (tp:TargetPair)
WHERE tp.name IS NOT NULL AND trim(tp.name) <> ''
OPTIONAL MATCH (tp)-[:HAS_TARGET]-(t:Target)
RETURN tp.name AS name, collect(DISTINCT t.symbol) AS targets
ORDER BY name
""",
        enforce_limit=False,
    )
    merged: dict[str, set[str]] = {}
    for row in rows:
        name = row.get("name")
        if isinstance(name, str) and name.strip():
            merged.setdefault(name, set()).update(
                t for t in row.get("targets", []) if isinstance(t, str) and t.strip()
            )
    return [TargetPairOption(name, tuple(sorted(targets))) for name, targets in sorted(merged.items())]


def _normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


def _parse_known_targets(query: str, known: set[str]) -> set[frozenset[str]]:
    """Parse only complete known symbols; preserve compound symbols and ambiguity."""
    symbols = sorted(known, key=lambda s: (-len(s), s))

    @lru_cache(maxsize=None)
    def parse(rest: str) -> frozenset[frozenset[str]]:
        if not rest:
            return frozenset({frozenset()})
        results = set()
        for symbol in symbols:
            if not rest.startswith(symbol):
                continue
            tail = rest[len(symbol):]
            if tail and tail[0] not in " /":
                continue
            for suffix in parse(tail.lstrip(" /")):
                results.add(suffix | {symbol})
        return frozenset(results)

    return set(parse(query))


def search_target_pairs(options: Iterable[TargetPairOption], query: str) -> list[str]:
    options = list(options)
    query = _normalize(query)
    if not query:
        return sorted(option.name for option in options)
    members = {o.name: {_normalize(t) for t in o.targets} for o in options}
    known = set().union(*members.values()) if members else set()
    # A complete standard combination name is never split to infer membership.
    exact = {o.name for o in options if _normalize(o.name) == query}
    if exact:
        wanted = {frozenset(members[name]) for name in exact if members[name]}
    elif query in known:
        wanted = {frozenset({query})}
    else:
        wanted = _parse_known_targets(query, known)
    ranked = []
    for option in options:
        targets = members[option.name]
        if option.name in exact:
            rank = 0
        elif wanted and any(w <= targets for w in wanted):
            rank = 1 if any(w == targets for w in wanted) else 2
        elif not wanted and all(
            (part in targets if part in known else
             any(part in target for target in targets) or part in _normalize(option.name))
            for part in query.split()
        ):
            rank = 3
        else:
            continue
        ranked.append((rank, option.name))
    return [name for _, name in sorted(ranked)]


def validate_target_pair_selection(value: str | None, candidates: Iterable[str]) -> str:
    if not value or value not in candidates:
        raise ValueError("Select an existing combination before generating a report.")
    return value


def validate_current_target_pair(runner: Any, value: str) -> None:
    rows = runner.run(
        "MATCH (tp:TargetPair {name: $value}) RETURN count(tp) AS count",
        {"value": value},
    )
    if not value.strip() or not rows or not rows[0].get("count"):
        raise ValueError("This combination is no longer available. Refresh combinations and select again.")
