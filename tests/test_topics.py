from pytest import mark, raises

from overcast.errors import ValidationError
from overcast.topics import Format, TopicSettings


def test_topic_settings_parse_creates_valid_object() -> None:
    topic_settings = TopicSettings.parse(
        name="AI News",
        prompt="Weekly digest of AI research",
        language="en",
        target_duration_minutes=30,
        format="dialogue",
    )

    assert topic_settings == TopicSettings(
        name="AI News",
        prompt="Weekly digest of AI research",
        language="en",
        target_duration_minutes=30,
        format=Format.DIALOGUE,
    )


def test_topic_settings_parse_applies_defaults() -> None:
    topic_settings = TopicSettings.parse(name="AI News", prompt="Weekly digest")

    assert topic_settings.language == "en"
    assert topic_settings.target_duration_minutes == 15
    assert topic_settings.format == Format.MONOLOGUE


def test_topic_settings_parse_normalizes_input() -> None:
    topic_settings = TopicSettings.parse(
        name="  AI News  ",
        prompt="\n Weekly digest \t",
        language=" EN ",
    )

    assert topic_settings.name == "AI News"
    assert topic_settings.prompt == "Weekly digest"
    assert topic_settings.language == "en"


@mark.parametrize("field", ["name", "prompt"])
@mark.parametrize("value", ["", "   ", "\n\t"])
def test_topic_settings_parse_rejects_blank_text(field: str, value: str) -> None:
    values = {"name": "AI News", "prompt": "Weekly digest"} | {field: value}

    with raises(ValidationError) as error:
        TopicSettings.parse(name=values["name"], prompt=values["prompt"])

    assert [issue.field for issue in error.value.issues] == [field]


@mark.parametrize("language", ["e", "eng", "en-US", "e1", "ру"])
def test_topic_settings_parse_rejects_invalid_language(language: str) -> None:
    with raises(ValidationError) as error:
        TopicSettings.parse(name="AI News", prompt="Weekly digest", language=language)

    assert [issue.field for issue in error.value.issues] == ["language"]


@mark.parametrize("duration", [1, 120])
def test_topic_settings_parse_accepts_duration_bounds(duration: int) -> None:
    topic_settings = TopicSettings.parse(
        name="AI News",
        prompt="Weekly digest",
        target_duration_minutes=duration,
    )

    assert topic_settings.target_duration_minutes == duration


@mark.parametrize("duration", [0, 121, -1])
def test_topic_settings_parse_rejects_duration_out_of_range(duration: int) -> None:
    with raises(ValidationError) as error:
        TopicSettings.parse(
            name="AI News",
            prompt="Weekly digest",
            target_duration_minutes=duration,
        )

    assert [issue.field for issue in error.value.issues] == ["target_duration_minutes"]


def test_topic_settings_parse_rejects_boolean_duration() -> None:
    with raises(ValidationError) as error:
        TopicSettings.parse(
            name="AI News",
            prompt="Weekly digest",
            target_duration_minutes=True,
        )

    assert [issue.field for issue in error.value.issues] == ["target_duration_minutes"]
    assert "boolean" in error.value.issues[0].message


@mark.parametrize("format", ["monologue", "dialogue"])
def test_topic_settings_parse_accepts_formats(format: str) -> None:
    topic_settings = TopicSettings.parse(
        name="AI News",
        prompt="Weekly digest",
        format=format,
    )

    assert topic_settings.format == Format(format)


@mark.parametrize("format", ["podcast", "Monologue", ""])
def test_topic_settings_parse_rejects_unknown_format(format: str) -> None:
    with raises(ValidationError) as error:
        TopicSettings.parse(name="AI News", prompt="Weekly digest", format=format)

    assert [issue.field for issue in error.value.issues] == ["format"]


def test_topic_settings_parse_collects_all_issues() -> None:
    with raises(ValidationError) as error:
        TopicSettings.parse(
            name=" ",
            prompt="",
            language="en_US",
            target_duration_minutes=1000,
            format="nothing",
        )

    fields = [issue.field for issue in error.value.issues]

    assert sorted(fields) == sorted(
        ["name", "prompt", "language", "target_duration_minutes", "format"]
    )


def test_validation_error_message_lists_fields() -> None:
    with raises(ValidationError) as error:
        TopicSettings.parse(name="", prompt="", target_duration_minutes=0)

    message = str(error.value)

    assert "name:" in message
    assert "prompt:" in message
    assert "target_duration_minutes:" in message


@mark.parametrize(
    ("name", "name_key"),
    [
        ("AI News", "ai news"),
        ("ai news", "ai news"),
        ("Новости ИИ", "новости ии"),
        ("Straße", "strasse"),
    ],
)
def test_topic_settings_name_key_ignores_case(name: str, name_key: str) -> None:
    topic_settings = TopicSettings.parse(name=name, prompt="Weekly digest")

    assert topic_settings.name_key == name_key
