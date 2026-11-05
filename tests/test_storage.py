import re
import sqlite3
from collections.abc import Iterator
from contextlib import closing
from importlib.resources import files
from pathlib import Path

from pytest import MonkeyPatch, fixture, mark, raises

from overcast.errors import StorageError
from overcast.storage import connect, initialize_database, migrate


@fixture
def connection() -> Iterator[sqlite3.Connection]:
    schema = files("overcast").joinpath("schema.sql").read_text(encoding="utf-8")
    connection = sqlite3.connect(":memory:", autocommit=True)

    try:
        connection.execute(schema)
        yield connection
    finally:
        connection.close()


@fixture
def empty_connection() -> Iterator[sqlite3.Connection]:
    with closing(sqlite3.connect(":memory:", autocommit=False)) as connection:
        yield connection


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


def test_initialize_database_rejects_newer_schema_version(tmp_path: Path) -> None:
    db_path = tmp_path / "app.sqlite"
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA user_version = 2")
    finally:
        connection.close()

    with raises(
        StorageError,
        match=re.escape(
            f"Can't initialize database {db_path}: unsupported schema version 2"
        ),
    ):
        initialize_database(db_path)

    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.execute("PRAGMA user_version")
        (db_version,) = cursor.fetchone()
        assert db_version == 2
    finally:
        connection.close()


def test_initialize_database_rejects_missing_parent_dir(tmp_path: Path) -> None:
    db_path = tmp_path / "missing" / "app.sqlite"

    with raises(StorageError, match=re.escape(f"Can't open database {db_path}:")):
        initialize_database(db_path)

    assert not db_path.parent.exists()


def test_initialize_database_rejects_non_database_file(tmp_path: Path) -> None:
    db_path = tmp_path / "app.sqlite"
    db_path.write_text("keep me", encoding="utf-8")

    with raises(StorageError, match=re.escape(f"Can't initialize database {db_path}:")):
        initialize_database(db_path)

    assert db_path.read_text(encoding="utf-8") == "keep me"


def test_connect_creates_missing_file(tmp_path: Path) -> None:
    db_path = tmp_path / "app.sqlite"

    with closing(connect(db_path, create=True)):
        pass

    assert db_path.is_file()


@mark.parametrize("create", [True, False])
def test_connect_opens_existing_database(tmp_path: Path, create: bool) -> None:
    db_path = tmp_path / "app.sqlite"
    with closing(sqlite3.connect(db_path, autocommit=True)) as connection:
        connection.execute("CREATE TABLE notes (text TEXT)")
        connection.execute("INSERT INTO notes VALUES ('keep me')")

    with closing(connect(db_path, create=create)) as connection:
        rows = connection.execute("SELECT text FROM notes").fetchall()

    assert rows == [("keep me",)]


def test_connect_rejects_missing_file_without_create(tmp_path: Path) -> None:
    db_path = tmp_path / "app.sqlite"

    with raises(StorageError, match=re.escape(f"Can't open database {db_path}:")):
        connect(db_path)

    assert not db_path.exists()


def test_connect_keeps_special_characters_in_file_name(tmp_path: Path) -> None:
    db_path = tmp_path / "my db?#%1.sqlite"

    with closing(connect(db_path, create=True)):
        pass

    assert list(tmp_path.iterdir()) == [db_path]


def test_connect_accepts_relative_path(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with closing(connect(Path("app.sqlite"), create=True)):
        pass

    assert (tmp_path / "app.sqlite").is_file()


def test_migrate_applies_schema(empty_connection: sqlite3.Connection) -> None:
    migrate(empty_connection)

    # Querying after migrate also guards against migrate closing the connection.
    tables = empty_connection.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table'"
    ).fetchall()
    (db_version,) = empty_connection.execute("PRAGMA user_version").fetchone()

    assert tables == [("topics",)]
    assert db_version == 1


def test_migrate_accepts_current_version(empty_connection: sqlite3.Connection) -> None:
    migrate(empty_connection)
    migrate(empty_connection)

    (db_version,) = empty_connection.execute("PRAGMA user_version").fetchone()

    assert db_version == 1


def test_migrate_rejects_unsupported_version(
    empty_connection: sqlite3.Connection,
) -> None:
    empty_connection.execute("PRAGMA user_version = 2")

    with raises(StorageError, match=re.escape("unsupported schema version 2")):
        migrate(empty_connection)

    tables = empty_connection.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table'"
    ).fetchall()

    assert tables == []
