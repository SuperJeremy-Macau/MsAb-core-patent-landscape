from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReportTable:
    title: str
    rows: list[dict[str, Any]]

    @property
    def columns(self) -> list[str]:
        columns: list[str] = []
        for row in self.rows:
            for key in row:
                if key not in columns:
                    columns.append(key)
        return columns


@dataclass
class ReportSection:
    title: str
    body: str
    tables: list[ReportTable] = field(default_factory=list)


@dataclass
class PatentLandscapeReport:
    report_type: str
    input_value: str
    title: str
    generated_at: str
    sections: list[ReportSection]
    provenance: dict[str, Any]
    query_row_counts: dict[str, int]
    query_results: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
