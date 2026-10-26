import sqlite3
from importlib.resources import files
from pathlib import Path


def check_database(db_path: Path) -> tuple[int] | None:
    connection = sqlite3.connect(db_path, autocommit=True)

    try:
        cursor = connection.execute("SELECT 1")
        return cursor.fetchone()
    finally:
        connection.close()


def initialize_database(db_path: Path) -> None:
    schema = files("overcast").joinpath("schema.sql").read_text(encoding="utf-8")
    connection = sqlite3.connect(db_path, autocommit=False)

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
                raise RuntimeError(f"Unsupported schema version: {current_db_version}")

    finally:
        connection.close()
