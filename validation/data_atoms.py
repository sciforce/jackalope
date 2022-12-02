# Copyrigt 2022 Sciforce
from __future__ import annotations
from dataclasses import dataclass
import pydantic
from core import ontology
from core import data_model
from utils.constants import CONCEPT_MODEL_ATTRIBUTE
from utils.constants import UNAPPROVED_ATTRIBUTE
from utils.constants import ALLOW_UNAPPROVED
from typing import Optional

validation_logger = ontology.onto_logger.getChild('Validation')


Cardinality = tuple[int, int | None]


class SNOMEDConcept(pydantic.BaseModel):
    id: int
    ontology: ontology.Ontology

    @pydantic.root_validator
    @classmethod
    def check_in_ontology(cls, values):
        # Check if concept is a node in ontology object
        if values['id'] not in values['ontology']:
            raise ValueError(f"Concept {values['id']} is not a valid code in the ontology")
        return values

    def get(self) -> int:
        return self.id

    class Config:
        arbitrary_types_allowed = True


class ValidatedRelationship(pydantic.BaseModel):
    typeId: int
    destinationId: Optional[int]
    concreteValue: Optional[str | int | float | bool]
    parent_ontology: ontology.Ontology

    @pydantic.root_validator()
    @classmethod
    def check_type_is_attribute(cls, values):
        ont: ontology.Ontology = values['parent_ontology']
        v: int = values['typeId']
        if ont.is_descendant(v, UNAPPROVED_ATTRIBUTE):
            if not ALLOW_UNAPPROVED:
                raise ValueError(f"Use of unapproved attributes is forbidden: {v}")
            else:
                validation_logger.warning(f"Used an unapproved attribute: {v}")
        if not ont.is_descendant(v, CONCEPT_MODEL_ATTRIBUTE):
            raise ValueError("SCTID does not belongs to an attribute")
        return values

    def get(self) -> data_model.Relationship | data_model.ConcreteRelationship:
        if self.destinationId is not None:
            return data_model.Relationship(self.typeId, self.destinationId)
        if self.concreteValue is not None:
            return data_model.ConcreteRelationship(self.typeId, self.concreteValue)
        raise ValueError("Relationship has no destination or concrete value")

    class Config:
        arbitrary_types_allowed = True


@dataclass(frozen=True)
class DomainRule:
    id: int
    attributeId: int
    domainId: int
    grouped: bool  # Ignored: only OWL cares about this
    attribute_cardinality: Cardinality
    attribute_in_group_cardinality: Cardinality
    mandatory: bool


@dataclass(frozen=True)
class RangeRule:
    # This depends on a whole different syntax, so will not be implemented for now.
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Range rules are not implemented yet")


# Specific expression errors
class SNOMEDExpressionsError(Exception):
    pass


class SCTIDInvalid(SNOMEDExpressionsError):
    def __init__(self, sctid: int):
        super().__init__(f"Invalid SCTID: {sctid}")
        self.sctid = sctid


class MRCMValidationError(SNOMEDExpressionsError):
    def __init__(self, message: str, rule: DomainRule):
        super().__init__(message, rule)
        self.message = message
        self.rule = rule
