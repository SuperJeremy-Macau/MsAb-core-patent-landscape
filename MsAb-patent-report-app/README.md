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
