import sqlite3
from collections.abc import Iterator
from importlib.resources import files
from pathlib import Path

from pytest import fixture, raises

from overcast.storage import check_database


@fixture
def connection() -> Iterator[sqlite3.Connection]:
    schema = files("overcast").joinpath("schema.sql").read_text(encoding="utf-8")
    connection = sqlite3.connect(":memory:", autocommit=True)

    try:
        connection.execute(schema)
        yield connection
    finally:
        connection.close()


def test_check_storage(tmp_path: Path) -> None:
    path = tmp_path / "app.sqlite"
    result = check_database(path)

    assert path.is_file()
    assert result == (1,)


def test_check_missing_dir(tmp_path: Path) -> None:
    path = tmp_path / "missing" / "app.sqlite"

    with raises(sqlite3.OperationalError):
        check_database(path)

    assert not path.parent.exists()


def test_topics_rejects_zero_duration(connection: sqlite3.Connection) -> None:
    with raises(sqlite3.IntegrityError):
        connection.execute(
            """
                INSERT INTO topics (name, prompt, language, target_duration_minutes, format, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "test name",
                "test prompt",
                "en",
                0,
                "dialogue",
                "2026-10-22T17:01:10Z",
                "2026-10-22T17:01:10Z",
            ),
        )


def test_topics_stores_valid_topic(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
            INSERT INTO topics (name, prompt, language, target_duration_minutes, format, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "test name",
            "test prompt",
            "en",
            10,
            "dialogue",
            "2026-10-22T17:01:10Z",
            "2026-10-22T17:01:10Z",
        ),
    )

    cursor = connection.execute(
        """
            SELECT name, target_duration_minutes FROM topics
        """
    )

    row = cursor.fetchone()

    assert row == ("test name", 10)
