import sqlite3
from collections.abc import Iterator
from importlib.resources import files
from pathlib import Path

from pytest import fixture, raises

from overcast.storage import initialize_database


@fixture
def connection() -> Iterator[sqlite3.Connection]:
    schema = files("overcast").joinpath("schema.sql").read_text(encoding="utf-8")
    connection = sqlite3.connect(":memory:", autocommit=True)

    try:
        connection.execute(schema)
        yield connection
    finally:
        connection.close()


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


def test_initialize_database_persists_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "app.sqlite"
    initialize_database(db_path)

    connection = sqlite3.connect(db_path, autocommit=True)
    try:
        cursor = connection.execute(
            """
                SELECT name FROM sqlite_schema
                WHERE type = 'table' AND name = 'topics'
            """
        )
        row = cursor.fetchone()

        assert row == ("topics",)

        cursor = connection.execute("PRAGMA user_version")
        row = cursor.fetchone()

        assert row == (1,)

    finally:
        connection.close()


def test_reinitialize_database(tmp_path: Path) -> None:
    db_path = tmp_path / "app.sqlite"
    initialize_database(db_path)
    connection = sqlite3.connect(db_path, autocommit=True)

    try:
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
    finally:
        connection.close()

    initialize_database(db_path)
    connection = sqlite3.connect(db_path, autocommit=True)

    try:
        cursor = connection.execute(
            """
                SELECT name FROM topics
            """
        )
        topic = cursor.fetchone()

        assert topic == ("test name",)

        cursor = connection.execute("PRAGMA user_version")
        (db_version,) = cursor.fetchone()

        assert db_version == 1

    finally:
        connection.close()
