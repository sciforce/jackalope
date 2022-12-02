from utils import hashing
from utils.constants import HASH_COMPATIBILITY_VERSION
from random import randint
from utils.constants import OMOP_CODE_FIELD_LENGTH


def test_hashing_code():
    assert hashing.jackalope_hash_code(
            'test_string',
            HASH_COMPATIBILITY_VERSION
        ) == 'e7bc867c5d56acdf0fa0ff4b291d85137c375142234f580a68'
    assert len(hashing.jackalope_hash_code(str(randint(0, 1000000)))) == OMOP_CODE_FIELD_LENGTH // 2
