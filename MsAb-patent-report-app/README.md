# MsAb Patent Report App

Streamlit MVP for generating deterministic multispecific and bispecific antibody patent landscape reports from the updated Neo4j knowledge graph.

## Report Lenses

- `Entity Lens`: `Target`, `TargetPair`, and `Company`.
- `Curated Knowledge Lens`: `Functional Role`, `Technology Class`, `Pathway`, and `Cancer Expression`.

Curated knowledge lenses start from manually curated biological or technical layers. Cancer-expression reports describe target expression context and should not be read as indication or clinical-use evidence.

## Run

```powershell
& 'E:\anconda\Scripts\conda.exe' run -n bsab-scidata streamlit run MsAb-patent-report-app\app.py
```

## Target Pair search

Choose `Target Pair`, enter one or more targets, select a matching database
combination, then click `Generate Report`. Multiple targets use AND matching;
order and case do not matter. Exact standard names rank first, and target
membership comes from `HAS_TARGET` relationships, including multi-target pairs.
Complete compound target symbols are preserved; slash-separated input is parsed
only through known symbols. Partial names can narrow candidates but never become
report inputs.

The catalogue loads every distinct nonblank `TargetPair.name`, without additional
exclusions or the report query row limit. It is cached for ten minutes; `Refresh
combinations` reloads it and clears the selection. Failed loads and unmatched
searches cannot submit. The report generator checks the chosen name against the
live database before running the unchanged report query bundle.

Validation on 2026-09-18: 948 loaded names matched the database count; `CD3`
matched 179 combinations (43 with more than two targets); all tested BCMA/CD3
input orders matched the same five candidates. Position 701 (`IL2RB/IL2RG`) and
`4-1BB/5T4` were searchable. The BCMA/CD3 report for 1987–2026 was identical to
the pre-change report except its generation timestamp (664 patents, 31 families).
These counts describe that database snapshot and are not application limits.

## Configuration

Use environment variables or an ignored local config file. Do not commit real credentials.

Environment variables:

- `MSAB_NEO4J_URI`
- `MSAB_NEO4J_USER`
- `MSAB_NEO4J_PASSWORD`
- `MSAB_NEO4J_DATABASE`

Copy `config/settings.example.yaml` to `config/settings.local.yaml` for local overrides.

## Tests

```powershell
& 'E:\anconda\Scripts\conda.exe' run -n bsab-scidata pytest MsAb-patent-report-app\tests -q
```

## Real Database Smoke Test

The smoke test reads local credentials from environment variables, `config/settings.local.yaml`, or the workspace-level `Env.txt` when present. It prints only report status and row counts.

```powershell
& 'E:\anconda\Scripts\conda.exe' run -n bsab-scidata python MsAb-patent-report-app\scripts\smoke_test_neo4j.py
```

Built-in smoke inputs:

- `Target`: `CD3`
- `TargetPair`: `BCMA/CD3`
- `Company`: `ROCHE HOLDING LTD.`
- `Functional Role`: `Oncology_Effector_Cell_Redirection`
- `Technology Class`: `Trans-Bridging Immune Engagers`
- `Pathway`: `Adaptive Immune System`
- `Cancer Expression`: `Glioblastoma Multiforme`
