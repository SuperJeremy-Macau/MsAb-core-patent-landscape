from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings_loader import load_settings
from msab_patent_report.db.neo4j_runner import Neo4jRunner
from msab_patent_report.db.schema import fetch_database_snapshot, fetch_suggestions, fetch_year_range
from msab_patent_report.report.generator import generate_report
from msab_patent_report.target_pairs import (
    fetch_target_pairs,
    search_target_pairs,
    validate_target_pair_selection,
)
from msab_patent_report.ui.layout import (
    render_app_header,
    render_app_footer,
    render_empty_report_state,
    render_panel_heading,
    render_report,
    render_report_controls,
    render_snapshot_panel,
)
from msab_patent_report.ui.report_options import (
    DEFAULT_VALUES,
    REPORT_LENSES,
    REPORT_TYPE_DESCRIPTIONS,
    REPORT_TYPE_LABELS,
)
from msab_patent_report.ui.style import apply_app_style


SETTINGS_PATH = ROOT / "config" / "settings.example.yaml"


@st.cache_resource(show_spinner=False)
def get_runner() -> Neo4jRunner:
    cfg = load_settings(SETTINGS_PATH)
    neo = cfg["neo4j"]
    return Neo4jRunner(
        uri=neo["uri"],
        user=neo["user"],
        password=neo["password"],
        database=neo.get("database", "neo4j"),
        max_rows=int(neo.get("max_rows", 200)),
    )


@st.cache_data(show_spinner=False, ttl=600)
def cached_year_range() -> tuple[int, int]:
    return fetch_year_range(get_runner())


@st.cache_data(show_spinner=False, ttl=600)
def cached_suggestions(report_type: str) -> list[str]:
    return fetch_suggestions(get_runner(), report_type, limit=500)


@st.cache_data(show_spinner=False, ttl=600)
def cached_snapshot() -> dict:
    return fetch_database_snapshot(get_runner())


@st.cache_data(show_spinner=False, ttl=600)
def cached_target_pairs():
    return fetch_target_pairs(get_runner())


def target_pair_input(connected: bool) -> tuple[str | None, list[str]]:
    if st.button("Refresh combinations", disabled=not connected):
        cached_target_pairs.clear()
        st.session_state.pop("target_pair_selection", None)
    options = []
    try:
        if connected:
            options = cached_target_pairs()
    except Exception:
        st.error("Combinations could not be loaded. Refresh combinations to try again.")
    query = st.text_input(
        "Search by target(s) or combination name",
        key="target_pair_search",
        help="Enter one target or separate multiple targets with spaces.",
        max_chars=300,
    )
    candidates = search_target_pairs(options, query)
    if st.session_state.get("target_pair_selection") not in candidates:
        st.session_state["target_pair_selection"] = None
    selected = st.selectbox(
        "Select a matching combination",
        candidates,
        index=None,
        key="target_pair_selection",
        accept_new_options=False,
        disabled=not candidates,
        placeholder="Choose an existing combination",
    )
    st.caption(f"{len(candidates):,} matching / {len(options):,} available combinations")
    if not candidates and options:
        st.info("No matching combinations. Try a standard target name or fewer targets.")
    elif not options and connected:
        st.warning("No combinations are available. Refresh combinations to try again.")
    if not selected:
        st.caption("Select an existing combination before generating a report.")
    return selected, candidates


def _brief_error(exc: Exception) -> str:
    return " ".join(str(exc).split())[:700]


def main() -> None:
    st.set_page_config(page_title="MsAb Patent Report Console", layout="wide")
    apply_app_style()

    try:
        year_min, year_max = cached_year_range()
        snapshot = cached_snapshot()
        connected = True
        connection_error = None
    except Exception as exc:
        year_min, year_max = 1987, 2026
        snapshot = {}
        connected = False
        connection_error = _brief_error(exc)

    render_app_header(snapshot, connected, (year_min, year_max))

    left, center, right = st.columns([0.28, 0.50, 0.22], gap="medium")

    with left:
        with st.container(border=True):
            render_panel_heading("Report Setup")
            report_lens = st.segmented_control(
                "Report Lens",
                list(REPORT_LENSES),
                default="Entity Lens",
                help="Choose whether the report starts from an entity or from a curated knowledge layer.",
                width="stretch",
            )
            report_lens = report_lens or "Entity Lens"

            report_options = REPORT_LENSES[report_lens]
            report_type = st.segmented_control(
                "Report focus",
                report_options,
                default=report_options[0],
                format_func=lambda key: REPORT_TYPE_LABELS[key],
                key=f"report_focus_{report_lens}",
                help=REPORT_TYPE_DESCRIPTIONS[report_lens],
                width="stretch",
            )
            report_type = report_type or report_options[0]

            suggestions = []
            suggestion_error = None
            if connected and report_type != "TargetPair":
                try:
                    suggestions = cached_suggestions(report_type)
                except Exception as exc:
                    suggestion_error = _brief_error(exc)

            preferred = DEFAULT_VALUES[report_type]
            candidates = []
            if report_type == "TargetPair":
                selected, candidates = target_pair_input(connected)
            elif suggestions:
                index = suggestions.index(preferred) if preferred in suggestions else 0
                selected = st.selectbox(
                    "Report input value",
                    suggestions,
                    index=index,
                    accept_new_options=True,
                    help=REPORT_TYPE_DESCRIPTIONS[report_type],
                )
            else:
                selected = st.selectbox(
                    "Report input value",
                    [preferred],
                    index=0,
                    accept_new_options=True,
                    help=REPORT_TYPE_DESCRIPTIONS[report_type],
                )
                if suggestion_error:
                    st.warning("Suggestions are unavailable for this report focus.")
                    with st.expander("Suggestion detail"):
                        st.code(suggestion_error)

            value = str(selected or "") if report_type == "TargetPair" else str(selected or preferred)
            generate = st.button(
                "Generate Report", type="primary", width="stretch",
                disabled=not connected or (report_type == "TargetPair" and selected not in candidates),
            )

            with st.expander("Year filter", expanded=False):
                selected_years = st.slider(
                    "Publication year range",
                    min_value=year_min,
                    max_value=year_max,
                    value=(year_min, year_max),
                )

    if generate:
        with st.spinner("Running fixed Neo4j query bundle and assembling report..."):
            try:
                if report_type == "TargetPair":
                    validate_target_pair_selection(value, candidates)
                cfg = load_settings(SETTINGS_PATH)
                report = generate_report(
                    runner=get_runner(),
                    report_type=report_type,
                    value=value if report_type == "TargetPair" else value.strip(),
                    year_min=selected_years[0],
                    year_max=selected_years[1],
                    provenance={
                        "database": cfg.get("neo4j", {}).get("database", "neo4j"),
                        "source": "Neo4j knowledge graph",
                    },
                )
                st.session_state["report"] = report
            except Exception as exc:
                st.session_state.pop("report", None)
                center.error(f"Report generation failed: {_brief_error(exc)}")

    report = st.session_state.get("report")
    with center:
        with st.container(border=True):
            if report:
                render_report(report)
            else:
                render_empty_report_state(snapshot, (year_min, year_max))

    with right:
        with st.container(border=True):
            if report:
                render_report_controls(report)
            else:
                render_panel_heading("Report Controls", "Evidence, provenance, and export after generation.")
                st.caption("Waiting for a generated report.")
                if connected:
                    st.write("Connection: `read-only`")
                    st.write(f"Year range: `{year_min}-{year_max}`")
                else:
                    st.write("Connection: `unavailable`")
                st.divider()
                render_snapshot_panel(snapshot, connected, connection_error)

    render_app_footer()


if __name__ == "__main__":
    main()
