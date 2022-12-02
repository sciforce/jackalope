# Copyright 2022 Sciforce Ukraine. All rights reserved.
import hashlib
from utils.constants import HASH_COMPATIBILITY_VERSION
from utils.constants import OMOP_CODE_FIELD_LENGTH


def jackalope_hash_id(string_to_hash: str, key: bytes | None = HASH_COMPATIBILITY_VERSION) -> int:
    hasher = hashlib.blake2b(key=key, usedforsecurity=False)
    hasher.update(string_to_hash.encode('utf-8'))
    return int(hasher.hexdigest(), base=16)


def jackalope_hash_code(string_to_hash: str, key: bytes | None = HASH_COMPATIBILITY_VERSION) -> str:
    hasher = hashlib.blake2b(
        key=key,
        usedforsecurity=False,
        digest_size=OMOP_CODE_FIELD_LENGTH // 2  # in hexadecimal 1 byte fits in 2 characters
        )
    hasher.update(string_to_hash.encode('utf-8'))
    return hasher.hexdigest()
