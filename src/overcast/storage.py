import sqlite3
from importlib.resources import files
from pathlib import Path

from overcast.errors import StorageError


def initialize_database(db_path: Path) -> None:
    schema = files("overcast").joinpath("schema.sql").read_text(encoding="utf-8")
    try:
        connection = sqlite3.connect(db_path, autocommit=False)
    except sqlite3.Error as error:
        raise StorageError(f"Can't open database {db_path}: {error}") from error

    try:
        with connection:
            cursor = connection.execute("PRAGMA user_version")
            (current_db_version,) = cursor.fetchone()

            if current_db_version == 0:
                connection.execute(schema)
                connection.execute("PRAGMA user_version = 1")

            elif current_db_version == 1:
                pass

            else:
                raise StorageError(
                    f"Database {db_path} has unsupported schema version "
                    f"{current_db_version}"
                )
    except sqlite3.Error as error:
        raise StorageError(f"Can't initialize database {db_path}: {error}") from error
    finally:
        connection.close()
