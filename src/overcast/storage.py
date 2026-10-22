import sqlite3
from pathlib import Path


def check_database(db_path: Path) -> tuple[int] | None:
    connection = sqlite3.connect(db_path, autocommit=True)

    try:
        cursor = connection.execute("SELECT 1")
        return cursor.fetchone()
    finally:
        connection.close()
