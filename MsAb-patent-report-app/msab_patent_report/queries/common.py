from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class QueryDefinition:
    name: str
    description: str
    cypher: str
    default_limit: int = 50


def bundle_to_dict(bundle: Iterable[QueryDefinition]) -> dict[str, QueryDefinition]:
    return {query.name: query for query in bundle}
