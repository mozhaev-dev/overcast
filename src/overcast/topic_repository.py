import sqlite3
from datetime import datetime, timedelta
from sqlite3 import Connection, Cursor, Row
from typing import Any, Final

from overcast.errors import FieldIssue, IdCollisionError, StorageError, ValidationError
from overcast.topics import Format, Topic, TopicSettings, make_name_key

SELECT_TOPICS: Final[str] = """
    SELECT
        id, name, prompt, language, target_duration_minutes, format, created_at, updated_at
    FROM
        topics
"""


class TopicRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def add(self, topic: Topic) -> None:
        settings = topic.settings

        try:
            self.connection.execute(
                """
                INSERT INTO topics (
                    id, name, name_key, prompt, language, target_duration_minutes, format, created_at, updated_at
                ) VALUES (
                    :id, :name, :name_key, :prompt, :language, :target_duration_minutes, :format, :created_at, :updated_at
                )
                """,
                {
                    "id": topic.id,
                    "name": settings.name,
                    "name_key": settings.name_key,
                    "prompt": settings.prompt,
                    "language": settings.language,
                    "target_duration_minutes": settings.target_duration_minutes,
                    "format": settings.format,
                    "created_at": _to_db_timestamp(topic.created_at),
                    "updated_at": _to_db_timestamp(topic.updated_at),
                },
            )
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorname == "SQLITE_CONSTRAINT_PRIMARYKEY":
                raise IdCollisionError(f"Topic id {topic.id} already exists") from error

            if error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
                issue = FieldIssue(
                    "name", f"a topic named {settings.name!r} already exists"
                )
                raise ValidationError((issue,)) from error

            raise

        except sqlite3.Error as error:
            raise StorageError(f"Can't add topic {topic.id}: {error}") from error

    def get(self, topic_id: str) -> Topic | None:
        row = self._fetch_one(f"{SELECT_TOPICS} WHERE id = ?", (topic_id,))
        return None if row is None else _row_to_topic(row)

    def get_by_name(self, name: str) -> Topic | None:
        row = self._fetch_one(
            f"{SELECT_TOPICS} WHERE name_key = ?", (make_name_key(name),)
        )
        return None if row is None else _row_to_topic(row)

    def list(self) -> list[Topic]:
        try:
            rows = self._cursor().execute(f"{SELECT_TOPICS} ORDER BY created_at")
            return [_row_to_topic(row) for row in rows]
        except sqlite3.Error as error:
            raise StorageError(f"Can't read topics: {error}") from error

    def _fetch_one(self, query: str, parameters: tuple[Any, ...]) -> Row | None:
        try:
            return self._cursor().execute(query, parameters).fetchone()
        except sqlite3.Error as error:
            raise StorageError(f"Can't read topic: {error}") from error

    def _cursor(self) -> Cursor:
        cursor = self.connection.cursor()
        cursor.row_factory = Row
        return cursor


def _row_to_topic(row: Row) -> Topic:
    return Topic(
        id=row["id"],
        settings=TopicSettings(
            name=row["name"],
            prompt=row["prompt"],
            language=row["language"],
            target_duration_minutes=row["target_duration_minutes"],
            format=Format(row["format"]),
        ),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _to_db_timestamp(value: datetime) -> str:
    if value.utcoffset() != timedelta(0):
        raise ValueError(f"Timestamp must be timezone-aware UTC, got {value!r}")

    return value.isoformat()
