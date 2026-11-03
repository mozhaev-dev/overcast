from overcast.ids import new_id

ALPHABET = set("0123456789abcdefghjkmnpqrstvwxyz")


def test_new_id_returns_unique_values() -> None:
    ids = [new_id("topic") for _ in range(1000)]

    assert len(set(ids)) == len(ids)


def test_new_id_returns_prefixed_suffix() -> None:
    prefix = "test_prefix"
    generated = new_id(prefix)

    assert generated.startswith(f"{prefix}_")

    suffix = generated.removeprefix(f"{prefix}_")

    assert len(suffix) == 10
    assert set(suffix) <= ALPHABET
