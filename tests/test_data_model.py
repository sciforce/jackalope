import unittest
from core import data_model


class HierarchyMatch(unittest.TestCase):
    def test_mapping(self):
        test_match = data_model.HierarchicalMatch(0)
        self.assertTrue(test_match)
        self.assertTrue(test_match.mapped)

    def test_unrelated(self):
        test_match = data_model.HierarchicalMatch(-1)
        self.assertFalse(test_match)
        self.assertFalse(test_match.mapped)

    def test_related(self):
        test_match = data_model.HierarchicalMatch(5)
        self.assertTrue(test_match)
        self.assertFalse(test_match.mapped)

    def test_iadd(self):
        test_match_original = data_model.HierarchicalMatch(1)
        test_match_original += 1
        self.assertEqual(test_match_original.distance, 2)
        # Assert immutability
        test_match_copy = test_match_original
        test_match_original += 1
        self.assertIsNot(test_match_copy, test_match_original)

    def test_add(self):
        test_match_original = data_model.HierarchicalMatch(1)
        test_match_copy = test_match_original + 1
        self.assertEqual(test_match_copy.distance, 2)
        # Assert immutability
        self.assertIsNot(test_match_copy, test_match_original)


if __name__ == '__main__':
    unittest.main()
