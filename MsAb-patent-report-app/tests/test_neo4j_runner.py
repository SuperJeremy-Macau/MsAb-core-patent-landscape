import pytest
from neo4j.exceptions import ServiceUnavailable

from msab_patent_report.db.neo4j_runner import Neo4jRunner, assert_read_only_cypher, ensure_limit


def test_assert_read_only_rejects_write_keywords():
    with pytest.raises(ValueError):
        assert_read_only_cypher("MATCH (n) SET n.name = 'x'")


def test_assert_read_only_rejects_unrestricted_call():
    with pytest.raises(ValueError):
        assert_read_only_cypher("CALL db.labels()")


def test_ensure_limit_appends_default_limit():
    cypher = ensure_limit("MATCH (n) RETURN n", 25)
    assert cypher.endswith("LIMIT 25")


def test_ensure_limit_preserves_existing_limit():
    cypher = ensure_limit("MATCH (n) RETURN n LIMIT 5", 25)
    assert cypher.endswith("LIMIT 5")


class FlakySession:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def run(self, query, params):
        self.driver.run_calls += 1
        if self.driver.run_calls == 1:
            raise ServiceUnavailable("defunct connection")
        return [{"ok": 1}]


class FlakyDriver:
    def __init__(self):
        self.session_calls = 0
        self.run_calls = 0

    def session(self, database):
        self.session_calls += 1
        return FlakySession(self)


def test_runner_retries_once_after_transient_read_connection_failure():
    driver = FlakyDriver()
    runner = object.__new__(Neo4jRunner)
    runner._driver = driver
    runner._database = "neo4j"
    runner._max_rows = 200

    rows = runner.run("MATCH (n) RETURN n LIMIT 1")

    assert rows == [{"ok": 1}]
    assert driver.session_calls == 2
    assert driver.run_calls == 2
