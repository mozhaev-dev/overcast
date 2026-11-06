import sqlite3
from importlib.resources import files
from pathlib import Path
from types import TracebackType
from typing import Final, Self

from overcast.errors import StorageError
from overcast.topic_repository import TopicRepository

SCHEMA_VERSION: Final[int] = 1


class Storage:
    db_path: Path
    connection: sqlite3.Connection
    topics: TopicRepository

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def __enter__(self) -> Self:
        connection = connect(self.db_path)
        try:
            self._check_schema_version(connection)
        except BaseException:
            connection.close()
            raise

        self.connection = connection
        self.topics = TopicRepository(connection)

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            self.connection.rollback()
        except sqlite3.Error as error:
            raise StorageError(
                f"Can't roll back changes to database {self.db_path}: {error}"
            ) from error
        finally:
            self.connection.close()

    def commit(self) -> None:
        try:
            self.connection.commit()
        except sqlite3.Error as error:
            raise StorageError(
                f"Can't commit changes to database {self.db_path}: {error}"
            ) from error

    def _check_schema_version(self, connection: sqlite3.Connection) -> None:
        try:
            db_version = _read_current_db_version(connection)
        except sqlite3.Error as error:
            raise StorageError(
                f"Can't open database {self.db_path}: {error}"
            ) from error

        if db_version == 0:
            raise StorageError(f"Database {self.db_path} is not initialized")

        if db_version != SCHEMA_VERSION:
            raise StorageError(
                f"Database {self.db_path} has unsupported schema version {db_version}"
            )


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
            current_db_version = _read_current_db_version(connection)

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


def _read_current_db_version(connection: sqlite3.Connection) -> int:
    return connection.execute("PRAGMA user_version").fetchone()[0]
