# Copyright 2022 Sciforce Ukraine. All rights reserved.
from __future__ import annotations

from typing import Iterable

from utils import hashing
from core import data_model


class Expression:
    """Structure class to represent expression contents"""

    def __init__(self) -> None:
        self.definition_status = True
        self.parent_concepts = []
        self.relationship_groups = []
        self.concept_id = 0
        self.normalized: None | Expression = None
        self._cf_cache = None

    def __str__(self) -> str:
        s = ''
        s += str(self.concept_id) + ':\n'
        s += '\tParents:' + str(self.parent_concepts) + '\n'
        for i, group in enumerate(self.relationship_groups):
            s += '\tRelationship groups:\n'
            s += f'\t\t{i}:\n'
            for relationship in group:
                attribute = relationship.typeId
                try:
                    value = f"LITERAL: {relationship.concreteValue}"
                except AttributeError:
                    value = f"{relationship.destinationId}"
                s += f'\t\t\t{attribute} = {value}\n'
        s += '\n'
        return s

    def add_parent(self, parent) -> None:
        self.parent_concepts.append(parent)
        self.normalized = None

    def add_relationship_group(self, relationship_group) -> None:
        if not isinstance(relationship_group, data_model.RelationshipGroup):
            raise TypeError("relationship_group must be a RelationshipGroup object!")

        self.relationship_groups.append(relationship_group)
        self.normalized = None

    def set_definition_status(self, definition_status: bool) -> None:
        self.definition_status = definition_status
        self.normalized = None

    def normal_form(self, ont: data_model.OntologyInterface) -> Expression:
        """Infer attribute defintions and proximal primitives from all stated parents and return a new Expression """

        # If we have already normalized this expression, return the cached version
        if self.normalized is not None:
            return self.normalized

        # Collect proximal primitive parents, ungroupped attributes and separated attribute groups
        new_parents: set[int] = set()
        parent_attrs: list[data_model.MetaRelationship] = []
        parent_groups: list[data_model.RelationshipGroup] = []

        # Collect definitions from stated parents first
        for stated_parent in self.parent_concepts:
            # First, infer the proximal primitive ancestors from each of the stated parents:
            new_parents.update(ont.primitive_parents(stated_parent))

            # Next, get the attributes from each of the stated parents.
            # We will separate them into ungroupped attributes and attribute groups
            rels = list(ont.get_relationship_groups(stated_parent))

            # If there is exactly one group and no ungroupped attributes, demote to ungroupped.
            # This may violate "machine-readable concept model", but it does not matter for post-coordination purposes
            if len(rels) == 2 and not rels[0]:
                rels.pop(0)

            # Collect ungroupped relationships:
            try:
                ungroupped = rels[0].relationships
                parent_attrs.extend(ungroupped)

                try:
                    groups = rels[1:]
                    parent_groups.extend(groups)
                except IndexError:
                    # This allows concepts without any relationship groups
                    pass

            except IndexError:
                # This allows concepts without any relationships at all
                pass

        # Serialize RelationshipGroups to lists of MetaRelationships
        new_g = self._collect_relationships(parent_attrs, parent_groups)

        # Remove duplicates and redundancies, upsert groups:
        self._clean_relationships(ont, new_g)

        # Remove duplicates among parents, including redundant ancestors
        new_parents = ont.remove_redundant_parents(set(new_parents))

        # Generate an empty Expression object to hold the normalized form
        nnf = Expression()
        for parent in new_parents:
            nnf.add_parent(parent)

        # Add ungrouped attributes to the normalized form
        if 0 in new_g:

            # If there are multiple ungroupped attributes of the same type, elevate them to separate 1-of-group
            # Warninng: this is just an approximation of in-group-cardinality limitation
            # Correct implementation would consult these rules (represented in MRCM refsets):
            # https://confluence.ihtsdotools.org/display/DOCGLOSS/in+group+cardinality
            # However, this is not a problem for post-coordination purposes
            next_idx = max(new_g) + 1
            duplicating_rels = set()
            for i, rel in enumerate(new_g[0]):
                if i >= len(new_g[0]) - 1:
                    break

                for other_rel in new_g[0][i + 1:]:

                    if rel is other_rel:
                        continue

                    if (rel.typeId == other_rel.typeId and
                            not (rel.descends_from(other_rel, ont) or
                                 other_rel.descends_from(rel, ont))):
                        duplicating_rels.add(rel)
                        duplicating_rels.add(other_rel)

            for idx, rel in enumerate(duplicating_rels, start=next_idx):
                new_g[idx] = [rel]
                new_g[0].remove(rel)

        # If 0-group is empty and there is only one other group, demote all attributes to ungrouped
        g_keys = sorted(new_g)
        if len(g_keys) == 2 and not new_g[0]:
            g_keys.remove(0)

        # De-serialize groups to immutable RelationshipGroup objects
        for idx in g_keys:
            nnf.add_relationship_group(data_model.RelationshipGroup.freeze(new_g[idx]))

        # Infer definition status and share concept_id with the original expression
        nnf.concept_id = self.concept_id
        nnf.definition_status = self.definition_status

        # Remember nnf as normal, both for itself and this expression
        self.normalized = nnf
        nnf.normalized = nnf

        # Return the completed normalized form
        return nnf

    def _collect_relationships(self, parent_attrs: Iterable[data_model.MetaRelationship],
                               parent_groups: Iterable[data_model.RelationshipGroup]
                               ) -> data_model.RawRelationshipGroup:
        """Place together ungrouped relationships and the groups"""
        out = {0: []}

        # Fill in own stated relationships and add parent groups:
        for idx, group in enumerate(self.relationship_groups +
                                    list(parent_groups)):
            out[idx] = []
            out[idx].extend(group.relationships)

        # Extend the contents of the group 0:
        out[0].extend(parent_attrs)

        return out

    @staticmethod
    def _clean_relationships(ont: data_model.OntologyInterface,
                             relationship_groups: data_model.RawRelationshipGroup) -> None:
        """Mutate the groupped relationships, removing dublicates and redundancies"""

        # Remove duplicates and ancestors between ungroupped relationships:
        redundant = list()

        ungroupped_relationships = set(relationship_groups[0])
        for relationship in ungroupped_relationships:

            if relationship in redundant:
                continue

            for other_relationship in ungroupped_relationships:

                if relationship is other_relationship:
                    continue

                if other_relationship.descends_from(relationship, ont):
                    redundant.append(relationship)
                    break

        relationship_groups[0] = [r for r in ungroupped_relationships if r not in redundant]

        # Remove dublicating and redundant groups:
        if 1 in relationship_groups:

            redundant_groups = list()

            for number, group in relationship_groups.items():
                if number in redundant_groups or number == 0:
                    continue

                for number_2, group_2 in relationship_groups.items():

                    if number_2 in redundant_groups or number_2 == 0 or number == number_2:
                        continue

                    rg, rg2 = data_model.RelationshipGroup.freeze(group), data_model.RelationshipGroup.freeze(group_2)

                    if rg == rg2 and number > number_2:
                        redundant_groups.append(number)
                        continue

                    if rg2.descends_from(rg, ont):
                        redundant_groups.append(number)
                        continue

            for i in set(redundant_groups):
                del relationship_groups[i]

            # Replace in group attributes with ungroupped descendants
            remove = dict()
            insert = dict()

            for attribute in relationship_groups[0]:
                for number, group in relationship_groups.items():

                    if number == 0:
                        continue

                    for in_group in group:

                        # If ungroupped attributes are also present in groups, remove former
                        if attribute.descends_from(in_group, ont):
                            remove[number] = in_group
                            insert[number] = attribute
                            break

            # Execute the changes:
            for group, removed in remove.items():
                relationship_groups[group].remove(removed)
                relationship_groups[group].append(insert[group])
            for attribute in insert.values():
                relationship_groups[0].remove(attribute)

            # Remove redundnat ungroupped attributes that are present in groups:
            redundant = []
            for attribute in relationship_groups[0]:
                for group, rel_list in relationship_groups.items():

                    if group == 0 or attribute in redundant:
                        continue

                    for in_group in rel_list:
                        if in_group.descends_from(attribute, ont):
                            redundant.append(attribute)
                            break

            relationship_groups[0] = [r for r in relationship_groups[0] if r not in redundant]

    def canonical(self, ont: data_model.OntologyInterface, raw=False) -> str:
        """Returns a canonical form for hashing purposes. Raw parameter controls if thhe expression is to be
        normalized first. """
        if self._cf_cache is not None and not raw:
            return self._cf_cache

        normal = self if raw else self.normal_form(ont)

        # Add definition status
        c_form = '===' if self.definition_status else "<<<"

        # Add parents:
        parents = sorted(normal.parent_concepts)
        c_form += '+'.join(str(p) for p in parents) + ':'

        # Add ungroupped relations:
        try:
            c_form += ','.join(rel.canonical() for rel
                               in normal.relationship_groups[0])
        except IndexError:
            pass

        # Add groupped relations:
        try:
            groups = sorted(normal.relationship_groups[1:])
            if c_form[-1] != ':':
                c_form += ','

            c_form += ','.join(group.canonical() for group in groups)
        except IndexError:
            pass

        if not raw:
            self._cf_cache = c_form
        return c_form

    def concept_id_tail(self, ont: data_model.OntologyInterface, length: int = 9) -> int:
        full_hash = hashing.jackalope_hash_id(self.canonical(ont))
        return full_hash % 10 ** length

    def hash_concept_code(self, ont: data_model.OntologyInterface) -> str:
        return hashing.jackalope_hash_code(self.canonical(ont))

    def substitute_sctid(self, old_id: int, new_id: int) -> None:
        self.relationship_groups = [group.substitute_sctid(old_id, new_id)
                                    for group in self.relationship_groups]
        self._cf_cache = None

    def get_attribute_counts(self,
                             use_ontology: data_model.OntologyInterface | None = None) -> dict[int, dict[int, int]]:
        """Returns a dictionary of attribute type ids and their counts per group in the expression.
        If "use_ontology" is not None, the counts are calculated with respect to subtype inheritance.
        """
        out = dict()
        # Add -1 group for total count independent of groups
        out[-1] = dict()
        for i, group in enumerate(self.relationship_groups):
            out[i] = dict()
            for rel in group.relationships:
                out[i][rel.typeId] = out.get(rel.typeId, 0) + 1
                out[-1][rel.typeId] = out[-1].get(rel.typeId, 0) + 1

        if use_ontology is not None:
            for group, cnts in out.items():
                for attr, cnt in cnts.items():
                    # Iterate over other attributes in the group. If any are descendants of the current attribute,
                    # add their counts to the current attribute's count.
                    for attr_2, cnt_2 in cnts.items():
                        if attr_2 == attr:
                            continue
                        if use_ontology.is_descendant(attr_2, attr):
                            cnt += cnt_2

        return out
