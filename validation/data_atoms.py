# Copyrigt 2022 Sciforce
from __future__ import annotations
from dataclasses import dataclass
import pydantic
from core import ontology
from core import data_model
from utils.constants import CONCEPT_MODEL_ATTRIBUTE
from utils.constants import UNAPPROVED_ATTRIBUTE
from utils.constants import ALLOW_UNAPPROVED
from utils.constants import ALLOW_NONRECOMMENDED
from typing import Optional

validation_logger = ontology.onto_logger.getChild('Validation')


Cardinality = tuple[int, int | None]


# noinspection PyMethodParameters
class SNOMEDConcept(pydantic.BaseModel):
    id: int
    ontology: ontology.Ontology

    @pydantic.validator('id')
    def check_in_ontology(cls, v, values):
        if v not in values['ontology']:
            raise ValueError(f'SCTID {v} does not represent an active concept')
        return v

    def get(self) -> int:
        return self.id


# noinspection PyMethodParameters
class ValidatedRelationship(pydantic.BaseModel):
    typeId: int
    destinationId: Optional[int]
    concreteValue: Optional[str | int | float | bool]
    parent_ontology: ontology.Ontology

    @pydantic.validator('typeId')
    def check_type_is_attribute(cls, v, values, **_):
        ont: ontology.Ontology = values['parent_ontology']
        if ont.is_descendant(v, UNAPPROVED_ATTRIBUTE):
            if not ALLOW_UNAPPROVED:
                raise ValueError(f"Use of unapproved attributes is forbidden: {v}")
            else:
                validation_logger.warning(f"Used an unapproved attribute: {v}")
        if not ont.is_descendant(v, CONCEPT_MODEL_ATTRIBUTE):
            raise ValueError("SCTID ddoes not belongs to an attribute")
        return v

    def get(self) -> data_model.Relationship | data_model.ConcreteRelationship:
        if self.destinationId is not None:
            return data_model.Relationship(self.typeId, self.destinationId)
        if self.concreteValue is not None:
            return data_model.ConcreteRelationship(self.typeId, self.concreteValue)


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
    raise NotImplementedError
