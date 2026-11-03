import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Final, Self

from overcast.errors import FieldIssue, ValidationError


class Format(StrEnum):
    MONOLOGUE = "monologue"
    DIALOGUE = "dialogue"


TOPIC_ID_PREFIX: Final[str] = "topic"

DEFAULT_LANGUAGE: Final[str] = "en"
DEFAULT_DURATION_MINUTES: Final[int] = 15
DEFAULT_FORMAT: Final[Format] = Format.MONOLOGUE

MIN_DURATION_MINUTES: Final[int] = 1
MAX_DURATION_MINUTES: Final[int] = 120
LANG_PATTERN: Final[str] = r"[a-z]{2}"


@dataclass(frozen=True, kw_only=True, slots=True)
class TopicSettings:
    name: str
    prompt: str
    language: str
    target_duration_minutes: int
    format: Format

    @property
    def name_key(self) -> str:
        return self.name.casefold()

    @classmethod
    def parse(
        cls,
        *,
        name: str,
        prompt: str,
        language: str | None = None,
        target_duration_minutes: int | None = None,
        format: str | None = None,
    ) -> Self:
        field_issues: list[FieldIssue] = []

        parsed_name = name.strip()
        if not parsed_name:
            field_issues.append(FieldIssue("name", "must not be empty"))

        parsed_prompt = prompt.strip()
        if not parsed_prompt:
            field_issues.append(FieldIssue("prompt", "must not be empty"))

        if language is not None:
            parsed_language = language.strip().lower()
            if not re.fullmatch(LANG_PATTERN, parsed_language):
                field_issues.append(
                    FieldIssue(
                        "language",
                        "must be a two-letter ISO 639-1 code such as en or de, "
                        f"got {language!r}",
                    )
                )
        else:
            parsed_language = DEFAULT_LANGUAGE

        if target_duration_minutes is not None:
            parsed_duration = target_duration_minutes
            if isinstance(parsed_duration, bool):
                field_issues.append(
                    FieldIssue(
                        "target_duration_minutes",
                        "must be an integer, not a boolean",
                    )
                )

            elif not MIN_DURATION_MINUTES <= parsed_duration <= MAX_DURATION_MINUTES:
                field_issues.append(
                    FieldIssue(
                        "target_duration_minutes",
                        f"must be between {MIN_DURATION_MINUTES} and "
                        f"{MAX_DURATION_MINUTES}, got {parsed_duration}",
                    )
                )
        else:
            parsed_duration = DEFAULT_DURATION_MINUTES

        if format is not None:
            try:
                parsed_format = Format(format)

            except ValueError:
                field_issues.append(
                    FieldIssue(
                        "format",
                        f"must be {Format.MONOLOGUE.value!r} or {Format.DIALOGUE.value!r}, "
                        f"got {format!r}",
                    )
                )

                parsed_format = DEFAULT_FORMAT
        else:
            parsed_format = DEFAULT_FORMAT

        if field_issues:
            raise ValidationError(tuple(field_issues))

        return cls(
            name=parsed_name,
            prompt=parsed_prompt,
            language=parsed_language,
            target_duration_minutes=parsed_duration,
            format=parsed_format,
        )


@dataclass(frozen=True, kw_only=True, slots=True)
class Topic:
    id: str
    settings: TopicSettings
    created_at: datetime
    updated_at: datetime
