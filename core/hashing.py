import hashlib
from typing import Optional

COMPATIBILITY_VERSION = b'1ALPHA'
FIELD_LENGTH = 50


def jackalope_hash_id(string_to_hash: str, key: Optional[bytes] = COMPATIBILITY_VERSION) -> int:
    hasher = hashlib.blake2b(key=key, usedforsecurity=False)
    hasher.update(string_to_hash.encode('utf-8'))
    return int(hasher.hexdigest(), base=16)


def jackalope_hash_code(string_to_hash: str, key: Optional[bytes] = COMPATIBILITY_VERSION) -> str:
    hasher = hashlib.blake2b(
        key=key,
        usedforsecurity=False,
        digest_size=FIELD_LENGTH//2  # in hexadecimal 1 byte fits in 2 characters
        )
    hasher.update(string_to_hash.encode('utf-8'))
    return hasher.hexdigest()
