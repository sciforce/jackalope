# Copyright 2022 Sciforce Ukraine. All rights reserved.
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Protocol, Iterator, Any
import typing
import pandas as pd


@typing.runtime_checkable
class OntologyInterface(Protocol):
    mrcm_domain_df: pd.DataFrame
    version: dict[str, datetime.date]

    def is_descendant(self, concept_id: int, ancestor_id: int) -> HierarchicalMatch:
        ...

    def is_primitive(self, concept_id: int) -> bool:
        ...

    def primitive_parents(self, concept_id: int) -> set[int]:
        ...

    def remove_redundant_parents(self, concept_ids: Iterable[int]) -> set[int]:
        ...

    def remove_redundant_children(self, concept_ids: Iterable[int]) -> set[int]:
        ...

    def expression_hierarchy(self, expression: Any) -> set[int]:
        ...

    def get_relationship_groups(self, concept_id: int) -> list[RelationshipGroup]:
        ...


class MetaRelationship(Protocol):
    typeId: int
    ord: int

    def descends_from(self, rel2: MetaRelationship, ont: OntologyInterface) -> HierarchicalMatch:
        ...

    def substitute_sctid(self, old_id: int, new_id: int) -> MetaRelationship:
        ...

    def canonical(self) -> str:
        ...


RawRelationshipGroup = dict[int, list[MetaRelationship]]


@dataclass(slots=True, frozen=True, order=True)
class HierarchicalMatch:
    """Logic package that contains information about hierarchical relation between two entities.

    * Distance value of -1 means absence of relation.
    * Distance value 0 means perfect semantic match.
    * Positive distance 1 means immediate parent relation.
    * Positive distance N means distant ancestorship relation.

    Implementation decides if shortest, longest or undetermined path is used for this value.
    """
    distance: int

    def __bool__(self) -> bool:
        return self.distance >= 0

    @property
    def mapped(self) -> bool:
        return self.distance == 0

    def __iadd__(self, other) -> HierarchicalMatch:
        return HierarchicalMatch(self.distance + other)

    def __add__(self, other) -> HierarchicalMatch:
        return HierarchicalMatch(self.distance + other)

    def __int__(self):
        return self.distance


@dataclass(frozen=True, order=True)
class Relationship:
    typeId: int
    destinationId: int
    ord: int = 1

    def descends_from(self, rel2: MetaRelationship, ont: OntologyInterface) -> HierarchicalMatch:
        # Never true for ConcreteRelationship:
        if not isinstance(rel2, type(self)):
            return HierarchicalMatch(-1)

        dist = 0
        if self.typeId != rel2.typeId:
            match = ont.is_descendant(self.typeId, rel2.typeId)
            if match:
                dist += match.distance
            else:
                return HierarchicalMatch(-1)

        if self.destinationId != rel2.destinationId:
            match = ont.is_descendant(self.destinationId, rel2.destinationId)
            if match:
                dist += match.distance
            else:
                return HierarchicalMatch(-1)

        return HierarchicalMatch(dist)

    def substitute_sctid(self, old_id: int, new_id: int) -> Relationship:
        if self.typeId == old_id:
            return Relationship(new_id, self.destinationId)
        if self.destinationId == old_id:
            return Relationship(self.typeId, new_id)
        return self

    def canonical(self) -> str:
        return str(self.typeId) + '=' + str(self.destinationId)


@dataclass(frozen=True, order=True)
class ConcreteRelationship:
    typeId: int
    concreteValue: str | int | float | bool
    ord: int = 2

    def descends_from(self, rel2: MetaRelationship, *_) -> HierarchicalMatch:
        if not isinstance(rel2, type(self)):
            return HierarchicalMatch(-1)

        # May only ever be True on exact value & attribute match:
        if (self.typeId, self.concreteValue) == (rel2.typeId, rel2.concreteValue):
            return HierarchicalMatch(0)

        return HierarchicalMatch(-1)

    def substitute_sctid(self, old_id: int, new_id: int) -> ConcreteRelationship:
        if self.typeId == old_id:
            return ConcreteRelationship(new_id, self.concreteValue)
        return self

    def canonical(self) -> str:
        if isinstance(self.concreteValue, bool):
            return str(self.typeId) + '=' + str(self.concreteValue).upper()

        elif isinstance(self.concreteValue, str):
            return str(self.typeId) + "='" + self.concreteValue + "'"

        else:  # Numeric
            return str(self.typeId) + "=#" + str(self.concreteValue)


@dataclass(frozen=True, order=True, slots=True)
class RelationshipGroup:
    relationships: tuple[MetaRelationship]

    def __bool__(self) -> bool:
        return bool(self.relationships)

    @classmethod
    def freeze(cls, rels: Iterable[MetaRelationship]) -> RelationshipGroup:
        # Sort manually, as relationships belong to different classes
        rel_classes = dict()
        for relationship in rels:
            try:
                rel_classes[type(relationship)].append(relationship)
            except KeyError:
                rel_classes[type(relationship)] = [relationship]

        all_classes = sorted(rel_classes, key=lambda x: (x.ord, x))

        sorted_rels = []
        for key in all_classes:
            sorted_rels.extend(sorted(rel_classes[key]))  # type: ignore

        return cls(tuple(sorted_rels))  # type: ignore

    def descends_from(
            self,
            relg2: RelationshipGroup,
            ont: OntologyInterface,
            addl_atrs: Iterable[MetaRelationship] | None = None,
            set_to_clear: set[MetaRelationship] | None = None) -> HierarchicalMatch:
        """
        We consider match successfull, if all attributes from parent have descendants among self;
        If matches were not found in group, check additional attributes.
        """
        addl_atrs = addl_atrs or list()

        distance = 0
        matched_from_relg2 = list()
        for relationship_1 in self:

            matched = False
            for relationship_2 in relg2:

                match = relationship_1.descends_from(relationship_2, ont)
                if match:
                    distance += match.distance
                    matched_from_relg2.append(relationship_2)
                    matched = True
                    break

            if not matched:
                for attribute in addl_atrs:
                    match = relationship_1.descends_from(attribute, ont)
                    if match:
                        # Using ungroupped attributes means that factual distance is at least 1 above the observed
                        distance += match.distance + 1
                        matched_from_relg2.append(attribute)

                        try:
                            set_to_clear.remove(attribute)
                        except KeyError:
                            pass

                        break

        if len(matched_from_relg2) == len(relg2.relationships):
            # Increase hierarchical distance for number of unmatched relationships, to prevent mapping
            if distance == 0:
                distance += len(self.relationships) - len(relg2.relationships)
            return HierarchicalMatch(distance)
        else:
            return HierarchicalMatch(-1)

    def substitute_sctid(self, old_id: int, new_id: int) -> RelationshipGroup:
        new_self = []
        for relationship in self:
            new_self.append(relationship.substitute_sctid(old_id, new_id))
        return RelationshipGroup.freeze(new_self)

    def canonical(self) -> str:
        s = '{'
        s += ','.join(rel.canonical() for rel in self)
        s += '}'

        return s

    def __iter__(self) -> Iterator[MetaRelationship]:
        return self.relationships.__iter__()
