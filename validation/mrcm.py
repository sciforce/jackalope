# Copyrigt 2022 Sciforce
from __future__ import annotations

from core import ontology
from core.expression import Expression
from utils.constants import ALLOW_NONRECOMMENDED
from utils import constants
from utils import logger
import validation.data_atoms

_logger = logger.jacka_logger.getChild('MRCMValidation')


def _parse_cardinality(cardinality: str) -> validation.data_atoms.Cardinality:
    if cardinality == '0..1':
        return 0, 1
    elif cardinality == '1..1':
        return 1, 1
    elif cardinality == '0..*':
        return 0, None
    elif cardinality == '1..*':
        return 1, None
    else:
        raise ValueError(f'Invalid cardinality: {cardinality}')


class MRCMValidator:

    def __init__(self, ont: ontology.Ontology) -> None:
        self.domain_rules: list[validation.data_atoms.DomainRule] = []
        self._snomed = ont

        for _, row in ont.mrcm_domain_df.iterrows():

            # Check if rule applies to PCEs:
            if not ont.is_descendant(row['contentTypeId'], constants.ALL_PCE_CONTENT):
                continue

            rule = validation.data_atoms.data_atoms.DomainRule(
                    id=row['id'],
                    attributeId=row['referencedComponentId'],
                    domainId=row['domainId'],
                    grouped=row['grouped'] == 1,
                    attribute_cardinality=_parse_cardinality(row['attributeCardinality']),
                    attribute_in_group_cardinality=_parse_cardinality(row['attributeInGroupCardinality']),
                    mandatory=row['ruleStrengthId'] == constants.MRCM_MANDATORY,
                    )

            self.domain_rules.append(rule)
        _logger.info(f'Loaded {len(self.domain_rules)} MRCM domain rules')
        _logger.debug(f'Mandatory rule count: {len([r for r in self.domain_rules if r.mandatory])}')
        _logger.debug(f'Optional rule count: {len([r for r in self.domain_rules if not r.mandatory])}')

    def validate_expression(self, e: Expression) -> None:
        # Count all attribute types and groups
        attr_types = e.get_attribute_counts(use_ontology=self._snomed)
        group_counts = {k: v for k, v in attr_types.items() if k > 0}
        parents = e.parent_concepts

        # Test if all mandatory attributes are present
        for rule in self.domain_rules:
            # Test if rule applies to expression parents
            if not any(self._snomed.is_descendant(p, rule.domainId) for p in parents):
                continue

            # Test if mandatory attribute is absent
            if rule.attribute_cardinality[0] > 0 and not any(self._snomed.is_descendant(a, rule.attributeId)
                                                             for a
                                                             in attr_types[-1]):
                err_msg = f'Obligatory attribute {rule.attributeId} is missing from expression {e}.'
                if rule.mandatory or not ALLOW_NONRECOMMENDED:
                    raise validation.data_atoms.MRCMValidationError(err_msg, rule)
                else:
                    _logger.warning(err_msg)
                    continue

            # Test total counts:
            for attr, total_count in attr_types[-1].items():

                # Test if rule applies to attribute
                if not self._snomed.is_descendant(attr, rule.attributeId):
                    continue

                # Test if attribute can belong to expression parents
                if not any(self._snomed.is_descendant(p, rule.domainId) for p in parents):
                    err_msg = f'Attribute {attr} is not allowed in expression {e}. ' \
                              f'Choose another attribute or add the expression parents.'
                    if rule.mandatory or not ALLOW_NONRECOMMENDED:
                        raise validation.data_atoms.MRCMValidationError(err_msg, rule)
                    else:
                        _logger.warning(err_msg)
                        continue

                # Test if attribute count is outside of cardinality
                if (rule.attribute_cardinality[1] is not None and total_count > rule.attribute_cardinality[1]) or \
                        total_count < rule.attribute_cardinality[0]:
                    err_msg = f'Attribute {attr} has {total_count} values, but should have between ' \
                              f'{rule.attribute_cardinality[0]} and {rule.attribute_cardinality[1] or "*"} values.'
                    if rule.mandatory or not ALLOW_NONRECOMMENDED:
                        raise validation.data_atoms.MRCMValidationError(err_msg, rule)
                    else:
                        _logger.warning(err_msg)
                        continue

            # Test in group counts:
            for group, group_attrs in group_counts.items():
                for attr, group_count in group_attrs.items():

                    # Test if rule applies to attribute
                    if not self._snomed.is_descendant(attr, rule.attributeId):
                        continue

                    # Test if attribute count is outside of cardinality
                    if (rule.attribute_in_group_cardinality[1] is not None and
                        group_count > rule.attribute_in_group_cardinality[1]) or group_count < \
                            rule.attribute_in_group_cardinality[0]:
                        err_msg = f'Attribute {attr} has {group_count} values in group {group}, but should have ' \
                                  f'between {rule.attribute_in_group_cardinality[0]} and ' \
                                  f'{rule.attribute_in_group_cardinality[1] or "*"} values.'
                        if rule.mandatory or not ALLOW_NONRECOMMENDED:
                            raise validation.data_atoms.MRCMValidationError(err_msg, rule)
                        else:
                            _logger.warning(err_msg)
                            continue
