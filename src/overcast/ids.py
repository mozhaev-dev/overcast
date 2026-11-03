import secrets
from typing import Final

ALPHABET: Final[str] = "0123456789abcdefghjkmnpqrstvwxyz"
LENGTH: Final[int] = 10


def new_id(prefix: str) -> str:
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(LENGTH))
    return f"{prefix}_{suffix}"
