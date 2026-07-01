from config.settings_loader import load_settings


def test_load_settings_merges_local_file_and_env(tmp_path, monkeypatch):
    base = tmp_path / "settings.yaml"
    local = tmp_path / "settings.local.yaml"
    base.write_text(
        "neo4j:\n"
        "  uri: bolt://base\n"
        "  user: neo4j\n"
        "  password: base\n"
        "  database: neo4j\n",
        encoding="utf-8",
    )
    local.write_text("neo4j:\n  uri: bolt://local\n", encoding="utf-8")
    monkeypatch.setenv("MSAB_NEO4J_PASSWORD", "from-env")

    cfg = load_settings(base)

    assert cfg["neo4j"]["uri"] == "bolt://local"
    assert cfg["neo4j"]["password"] == "from-env"


def test_load_settings_can_read_parent_env_txt(tmp_path, monkeypatch):
    base = tmp_path / "settings.yaml"
    env_file = tmp_path / "Env.txt"
    base.write_text("neo4j:\n  uri: ''\n  user: ''\n  password: ''\n  database: ''\n", encoding="utf-8")
    env_file.write_text(
        "neo4j:\n"
        "  uri: neo4j+s://example.databases.neo4j.io\n"
        "  user: neo4j\n"
        "  password: secret\n"
        "  database: neo4j\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("MSAB_NEO4J_URI", raising=False)
    monkeypatch.delenv("MSAB_NEO4J_PASSWORD", raising=False)

    cfg = load_settings(base, env_txt_path=env_file)

    assert cfg["neo4j"]["uri"] == "neo4j+s://example.databases.neo4j.io"
    assert cfg["neo4j"]["password"] == "secret"


def test_env_txt_neo4j_section_does_not_consume_later_unrelated_password(tmp_path, monkeypatch):
    base = tmp_path / "settings.yaml"
    env_file = tmp_path / "Env.txt"
    base.write_text("neo4j:\n  uri: ''\n  user: ''\n  password: ''\n  database: ''\n", encoding="utf-8")
    env_file.write_text(
        "neo4j:\n"
        "uri: neo4j+s://aura.example.databases.neo4j.io\n"
        "user: neo4j\n"
        "password: aura-password\n"
        "database: neo4j\n"
        "\n"
        "Local Neo4j:\n"
        "Connection URI:\n"
        "neo4j: bolt://localhost:7687\n"
        "password: local-password\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("MSAB_NEO4J_PASSWORD", raising=False)

    cfg = load_settings(base, env_txt_path=env_file)

    assert cfg["neo4j"]["uri"] == "neo4j+s://aura.example.databases.neo4j.io"
    assert cfg["neo4j"]["password"] == "aura-password"
