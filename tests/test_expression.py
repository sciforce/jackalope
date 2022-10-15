import unittest
from core import expression
from core import data_model


class Expression(unittest.TestCase):
    def setUp(self) -> None:
        self.expression = expression.Expression()

    def test_creation(self):
        self.assertTrue(self.expression)

    def test_add_parent(self):
        self.expression.add_parent(100)
        self.assertEqual(self.expression.parent_concepts, [100])

    def test_add_relationship_group(self):
        self.expression.add_relationship_group(data_model.RelationshipGroup(tuple()))
        self.assertEqual(self.expression.relationship_groups, [data_model.RelationshipGroup(tuple())])
        with self.assertRaises(TypeError):
            self.expression.add_relationship_group(None)

    def test_set_definition_status(self):
        self.assertTrue(self.expression.definition_status)
        self.expression.set_definition_status(False)
        self.assertFalse(self.expression.definition_status)
