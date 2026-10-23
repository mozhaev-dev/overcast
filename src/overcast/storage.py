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
            connection.execute(schema)
    finally:
        connection.close()
