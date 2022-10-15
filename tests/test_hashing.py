from core import hashing


def test_hashing_code():
    assert hashing.jackalope_hash_code('test_string') == 'e7bc867c5d56acdf0fa0ff4b291d85137c375142234f580a68'
