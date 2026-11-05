import sqlite3
from importlib.resources import files
from pathlib import Path
from typing import Final

from overcast.errors import StorageError

SCHEMA_VERSION: Final[int] = 1


def connect(db_path: Path, *, create: bool = False) -> sqlite3.Connection:
    mode = "rwc" if create else "rw"
    uri = f"{db_path.resolve().as_uri()}?mode={mode}"

    try:
        connection = sqlite3.connect(uri, uri=True, autocommit=False, timeout=5.0)
    except sqlite3.Error as error:
        raise StorageError(f"Can't open database {db_path}: {error}") from error

    return connection


def migrate(connection: sqlite3.Connection) -> None:
    try:
        with connection:
            cursor = connection.execute("PRAGMA user_version")
            (current_db_version,) = cursor.fetchone()

            if current_db_version == 0:
                connection.execute(_read_schema())
                connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

            elif current_db_version == SCHEMA_VERSION:
                pass

            else:
                raise StorageError(f"unsupported schema version {current_db_version}")
    except sqlite3.Error as error:
        raise StorageError(f"migration failed: {error}") from error


def initialize_database(db_path: Path) -> None:
    connection = connect(db_path, create=True)

    try:
        migrate(connection)
    except StorageError as error:
        raise StorageError(f"Can't initialize database {db_path}: {error}") from error
    finally:
        connection.close()


def _read_schema() -> str:
    return files("overcast").joinpath("schema.sql").read_text(encoding="utf-8")
