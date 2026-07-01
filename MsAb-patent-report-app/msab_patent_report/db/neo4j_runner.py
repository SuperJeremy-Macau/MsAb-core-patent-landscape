from __future__ import annotations

from typing import Any
import re

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired, TransientError


WRITE_PATTERNS = [
    r"\bCREATE\b",
    r"\bMERGE\b",
    r"\bDELETE\b",
    r"\bDETACH\s+DELETE\b",
    r"\bSET\b",
    r"\bDROP\b",
    r"\bLOAD\s+CSV\b",
    r"\bREMOVE\b",
    r"\bCALL\b",
    r"\bAPOC\.",
]


def assert_read_only_cypher(cypher: str) -> None:
    upper = cypher.upper()
    for pattern in WRITE_PATTERNS:
        if re.search(pattern, upper):
            raise ValueError(f"Cypher rejected by read-only guard: {pattern}")


def has_limit(cypher: str) -> bool:
    return re.search(r"\bLIMIT\s+\$?[A-Za-z0-9_]+", cypher, flags=re.IGNORECASE) is not None


def ensure_limit(cypher: str, max_rows: int) -> str:
    q = cypher.strip().rstrip(";")
    if has_limit(q):
        return q
    return f"{q}\nLIMIT {int(max_rows)}"


class Neo4jRunner:
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j", max_rows: int = 200):
        if not uri:
            raise ValueError("Neo4j URI is required.")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._database = database
        self._max_rows = int(max_rows)

    def close(self) -> None:
        self._driver.close()

    def run(
        self,
        cypher: str,
        params: dict[str, Any] | None = None,
        enforce_limit: bool = True,
    ) -> list[dict[str, Any]]:
        assert_read_only_cypher(cypher)
        query = ensure_limit(cypher, self._max_rows) if enforce_limit else cypher.strip().rstrip(";")
        for attempt in range(2):
            try:
                with self._driver.session(database=self._database) as session:
                    result = session.run(query, params or {})
                    return [dict(record) for record in result]
            except (ServiceUnavailable, SessionExpired, TransientError):
                if attempt == 1:
                    raise
        return []
