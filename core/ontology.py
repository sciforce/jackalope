# Copyright 2022 Sciforce Ukraine. All rights reserved.
from __future__ import annotations

import os
import pickle
from typing import Iterable
import datetime
import functools
import pathlib

import networkx as nx
import pandas as pd

from core import expression
from core import data_model
from utils.constants import DEFINED
from utils.constants import FSN
from utils.constants import ISA
from utils.constants import SCT_MODEL_COMPONENT
from utils.constants import SNOMED_ROOT
from utils.constants import SNOMED_US_MODULE
from utils.logger import jacka_logger
import validation.mrcm

onto_logger = jacka_logger.getChild('Ontology')


class AccidentalEquivalency(BaseException):
    """Error that represents assertion of full equivalency during ontology evaluation."""
    def __init__(self, sctid):
        self.sctid = sctid

    def __repr__(self):
        return f"Mapping to {self.sctid} must be done instead."


class Ontology(nx.DiGraph):
    concept_df: pd.DataFrame
    description_df: pd.DataFrame
    inferred_df: pd.DataFrame
    concrete_df: pd.DataFrame
    mrcm_range_df: pd.DataFrame
    mrcm_domain_df: pd.DataFrame
    module_dependency_df: pd.DataFrame
    concept_count: int
    version: dict[str, datetime.date]
    validator: validation.mrcm.MRCMValidator

    def _drop_frames(self):
        """Frees memory by relinquishing pandas DataFrame objects"""
        del self.concept_df
        del self.description_df
        del self.inferred_df
        del self.concrete_df
        del self.mrcm_range_df
        del self.mrcm_domain_df
        del self.module_dependency_df

    def dump(self, filepath: str | pathlib.Path, drop_raw_frames: bool = True):

        # Don't store raw dataframes (class attributes remain uninitialized)
        if drop_raw_frames is True:
            self._drop_frames()

        if not filepath.lower().endswith('.ont'):
            filepath += '.ont'

        with open(filepath, 'wb') as f:

            onto_logger.info(f"Dumping cache to {filepath}...")
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str | pathlib.Path) -> Ontology:
        with open(filepath, 'rb') as f:
            loaded = pickle.load(f)
            onto_logger.info(f"Loaded {cls} object containing {len(loaded)} concept entries.")

            return loaded

    @functools.cache
    def is_descendant(self, concept_id: int, ancestor_id: int) -> data_model.HierarchicalMatch:
        """Recursively look for a degree of relation between two concepts.
        Check is performed depth first, so the shortest path is not guaranteed. However, immediate ancestors are
        checked explicitly, so the result is always correct."""

        # Check equivalence
        if concept_id == ancestor_id:
            return data_model.HierarchicalMatch(0)

        # Check if a path exists
        if not nx.has_path(self, ancestor_id, concept_id):
            return data_model.HierarchicalMatch(-1)

        # Check immediate ancestorship
        if concept_id in self.successors(ancestor_id):
            return data_model.HierarchicalMatch(1)

        # Check if the concept is a descendant of the ancestor
        path_len = len(next(nx.all_simple_paths(self, ancestor_id, concept_id)))
        return data_model.HierarchicalMatch(path_len)

    @staticmethod
    def build(rf2_path: str | pathlib.Path) -> Ontology:
        """Returns a new Ontology from the RF2 files"""

        # Find files of interest in the directory
        onto_logger.info(f"Loading the ontology from {rf2_path}")

        def match_file(pattern: str, *parents: str) -> str:
            files = pathlib.Path(rf2_path).glob(os.path.join(*parents, pattern))
            onto_logger.info(f"Matching '{pattern}' in {parents[0]}...")

            for filename in files:
                if pattern in filename:
                    onto_logger.info(f"Found {filename} in {parents[0]}!")
                    return os.path.join(rf2_path, *parents, filename)

            raise FileNotFoundError(f"No match found for pattern {pattern}")

        # Terminology files
        concept_file_path = match_file("Concept", "Terminology")
        description_file_path = match_file("Description", "Terminology")
        inferred_relationship_file_path = match_file("_Relationship_", "Terminology")
        concrete_values_file_path = match_file("ConcreteValues", "Terminology")

        # Metadata files
        module_dependency_file_path = match_file("ModuleDependency", "Refset", "Metadata")
        mrcm_domain_file_path = match_file("MRCMAttributeDomain", "Refset", "Metadata")
        mrcm_range_file_path = match_file("MRCMAttributeRange", "Refset", "Metadata")

        # Initialize the new Ontology
        snomed = Ontology()

        onto_logger.info("Loading content frames...")
        snomed.concept_df = pd.read_csv(concept_file_path, delimiter='\t').query("active == 1")
        snomed.description_df = pd.read_csv(description_file_path, delimiter='\t').query("active == 1")
        snomed.inferred_df = pd.read_csv(inferred_relationship_file_path, delimiter='\t').query("active == 1")
        snomed.concrete_df = pd.read_csv(concrete_values_file_path, delimiter='\t').query("active == 1")

        onto_logger.info("Loading metadata frames...")
        snomed.mrcm_range_df = pd.read_csv(mrcm_range_file_path, delimiter='\t').query("active == 1")
        snomed.mrcm_domain_df = pd.read_csv(mrcm_domain_file_path, delimiter='\t').query("active == 1")
        snomed.module_dependency_df = pd.read_csv(module_dependency_file_path, delimiter='\t').query("active == 1")

        # Preserve dates of modules for versions check:
        def extract_date(module: int) -> datetime.date:
            try:
                idx = (snomed.module_dependency_df['moduleId'] == module) & \
                      (snomed.module_dependency_df['referencedComponentId'] == SCT_MODEL_COMPONENT)
                date_int, = snomed.module_dependency_df.loc[idx, 'effectiveTime']
                return datetime.date(
                    year=date_int // 10000,
                    month=date_int % 10000 // 100,
                    day=date_int % 100,
                    )
            except KeyError:
                onto_logger.warning(f"Did not find module {SNOMED_US_MODULE} "
                                    f"in Module Dependency. Defaulting to 1970-01-01")
                return datetime.date(1970, 1, 1)

        snomed.version = {'SNOMED CT US': extract_date(SNOMED_US_MODULE)}

        # Make sure we are dealing with a snapshot
        if snomed.concept_df.count()["id"] != snomed.concept_df.nunique()["id"]:
            raise ValueError('Non-unique concepts detected. Please use Snapshot instead of Full.')

        snomed.concept_count = len(snomed.concept_df)
        onto_logger.info(f"Found {snomed.concept_count} concepts.")

        return snomed

    def populate(self, dump_filename=None, isa_to_hierarchy: bool = True) -> None:
        """Populates the graph with concepts from the stored tables."""
        onto_logger.info("Populating the graph:")

        for rownum, concept in self.concept_df.iterrows():

            cid = concept["id"]
            # Counter:
            if rownum % 10000 == 0 or rownum == self.concept_count:  # type: ignore
                onto_logger.debug(f"On row {rownum} of {self.concept_count}...")

            # Get all names of the concept, extract the FSN
            names = self.description_df[self.description_df["conceptId"] == cid][["term", "typeId"]]

            try:
                fsn = names.query(f"typeId == {FSN}").iloc[0, 0]
            except IndexError:
                onto_logger.warning(f"WARNING: No FSN found for {cid}")
                fsn = "No FSN found"

            # Get all inferred relations of the concept and process them into Relationship objects
            rel = dict()

            # Classic relationships:
            for _, relationship in self.inferred_df[self.inferred_df["sourceId"] == cid].iterrows():
                r = data_model.Relationship(
                    destinationId=relationship['destinationId'],
                    typeId=relationship['typeId']
                    )

                # If required, add the 'Is a' as a node instead of is a relationship
                if isa_to_hierarchy and relationship.typeId == ISA:
                    self.add_edge(r.destinationId, cid)
                else:
                    rel[relationship["relationshipGroup"]] = rel.get(relationship["relationshipGroup"], list()) + [r]

            # Literal relationships:
            for _, relationship in self.concrete_df[self.concrete_df['sourceId'] == cid].iterrows():
                r = data_model.ConcreteRelationship(
                    typeId=relationship['typeId'],
                    concreteValue=float(relationship['value'][1:])
                    )

                rel[relationship["relationshipGroup"]] = rel.get(relationship["relationshipGroup"], list()) + [r]

            # If there are no 0-group relationships, add an empty group
            if 0 not in rel:
                rel[0] = []

            # Re-sort values: we need them by field value, not insertion order
            rel = {key: rel[key] for key in sorted(rel)}

            # Freeze the rel dict into a tuple of tuples
            frozen_rel = tuple(data_model.RelationshipGroup.freeze(r_in_group) for r_in_group in rel.values())

            concept_properties = {
                "full_specified_name": fsn,
                "relationships": frozen_rel,
                "definitionStatus": concept["definitionStatusId"] == DEFINED,
                "moduleId": concept["moduleId"],
                }

            self.add_node(cid, **concept_properties)

        onto_logger.info(f"Nodes added!")

        # Add MRCM constraints to the ontology
        self.validator = validation.mrcm.MRCMValidator(self)
        onto_logger.info("MRCM constraints added!")

        # If cache filename is specified, dump self to file
        if dump_filename is not None:
            self.dump(dump_filename)

    def classify(self):
        """Assigns the inferred_relationships for all concepts and builds hierarchy from axioms"""
        raise NotImplementedError

    def is_primitive(self, concept_id: int) -> bool:
        return not self.nodes[concept_id]['definitionStatus']

    @functools.lru_cache(maxsize=10_000)
    def primitive_parents(self, concept_id: int) -> set[int]:

        # Primitive concepts serve as their own PPP
        if self.is_primitive(concept_id):
            return {concept_id}

        proximal_primitive_parents = set()
        for node in self.predecessors(concept_id):
            if self.is_primitive(node):
                proximal_primitive_parents.add(node)

            else:
                proximal_primitive_parents.update(self.primitive_parents(node))

        return proximal_primitive_parents

    def remove_redundant_parents(self, concept_ids: Iterable[int]) -> set[int]:

        def is_redundant(parent) -> bool:
            for other_parent in concept_ids:
                if other_parent == parent:
                    continue

                if self.is_descendant(other_parent, parent):
                    return True

            return False

        new_parents = set(filter(lambda x: not is_redundant(x), concept_ids))
        return new_parents

    def remove_redundant_children(self, concept_ids: Iterable[int]) -> set[int]:

        def is_redundant(child) -> bool:
            for other_child in concept_ids:
                if other_child == child:
                    continue

                if self.is_descendant(child, other_child):
                    return True

            return False

        new_children = set(filter(lambda x: not is_redundant(x), concept_ids))
        return new_children

    def _validate_ancestorship(self, expr: expression.Expression,
                               concept_id: int) -> data_model.HierarchicalMatch:
        """Expression is considered a descendant of a given concept if:
            - All ungroupped attributes in the concept have descendants among any attributes in the expression
            - All concept groups are ancestors of groups in the expression
        """

        # If the concept is a parent of one of the stated parents:
        for parent in expr.parent_concepts:
            matched = self.is_descendant(parent, concept_id)
            if matched:
                return matched + 1

        # Primitive concepts do not get descendants assignment,
        if self.is_primitive(concept_id):
            return data_model.HierarchicalMatch(-1)

        # Check if all the concepts primitive parents are ancestors of at least one expression primitive parent:
        for c_parent in self.primitive_parents(concept_id):
            has_ancestor = any(self.is_descendant(e_parent, c_parent) for e_parent in expr.parent_concepts)
            if not has_ancestor:
                return data_model.HierarchicalMatch(-1)

        rel_groups = list(self.nodes[concept_id]['relationships'])

        # Redefine for concepts that only have one group and no ungroupped_attributes:
        if rel_groups[0] == data_model.RelationshipGroup.freeze(list()) and len(rel_groups) == 2:
            rel_groups.pop(0)

        hierarchical_distance = 0
        ungroupped_attributes = rel_groups[0].relationships
        unmatched_concept_attributes = set(ungroupped_attributes)
        unmatched_expression_attributes = set(expr.relationship_groups[0].relationships)

        # Traverse Expression attributes:
        all_attrs = []
        for group in expr.relationship_groups:
            all_attrs.extend(group.relationships)

        for c_rel in ungroupped_attributes:
            for e_rel in all_attrs:
                if c_rel in unmatched_concept_attributes:
                    match = e_rel.descends_from(c_rel, self)

                    if match:
                        hierarchical_distance += match.distance
                        unmatched_concept_attributes.remove(c_rel)
                        try:
                            unmatched_expression_attributes.remove(e_rel)
                        except KeyError:
                            pass
                        break

        if unmatched_concept_attributes:
            return data_model.HierarchicalMatch(-1)

        # Work with groupped relationships, if there are any:
        try:
            groups: list[data_model.RelationshipGroup] = list(rel_groups[1:])
        except IndexError:
            return data_model.HierarchicalMatch(hierarchical_distance)

        unmatched_groups = set(groups)
        matched_expression_groups = set()

        # Traverse Expression groups:
        for c_grp in groups:
            for e_grp in expr.relationship_groups:  # This does include group 0
                match = e_grp.descends_from(c_grp,
                                            self,
                                            addl_atrs=ungroupped_attributes,
                                            set_to_clear=unmatched_expression_attributes)
                if match:
                    matched_expression_groups.add(e_grp)
                    hierarchical_distance += match.distance
                    unmatched_groups.remove(c_grp)
                    break

        # Check if unmatched_groups can be cleaned up by inhering from the ungroupped attributes
        # This is, once again, approximation to avoid having to process the MRCM and will be rewritten
        for c_grp in unmatched_groups.copy():
            rel_count = len(c_grp.relationships)

            for rel in c_grp.relationships:
                for u_rel in ungroupped_attributes:
                    if rel.descends_from(u_rel, self):
                        rel_count -= 1

                        try:
                            unmatched_expression_attributes.remove(u_rel)
                        except KeyError:
                            pass

                        break
            if rel_count == 0:
                unmatched_groups.remove(c_grp)

        if unmatched_groups:
            return data_model.HierarchicalMatch(-1)
        else:
            # Unmatched groups & attributes add points of hierarchical distance
            if len(expr.relationship_groups) >= 2:
                hierarchical_distance += len(expr.relationship_groups) - len(matched_expression_groups)
            hierarchical_distance += len(unmatched_expression_attributes)
            return data_model.HierarchicalMatch(hierarchical_distance)

    def _check_concept_ancestorship(
            self,
            normal_form: expression.Expression,
            node: int,
            visited_nodes: set[int],
            ancestors: set[int],
            breadcrumb: None | list[int] = None) -> None:
        if breadcrumb is None:
            breadcrumb = list()

        # If the node was already reached by another breadcrumb trace, abort this one
        if node in visited_nodes:
            return
        visited_nodes.add(node)

        # If the node validates (is clean ancestor of the expression), continue to children;
        # otherwise, write the last reached node
        matches = self._validate_ancestorship(normal_form, node)
        if matches.mapped and normal_form.definition_status:
            raise AccidentalEquivalency(node)

        if matches:

            if self.successors(node):
                # Pass the breadcrumb trail to all descendants:
                breadcrumb.append(node)
                for child in self.successors(node):
                    self._check_concept_ancestorship(normal_form, child, visited_nodes, ancestors, breadcrumb)

            else:
                # Add current node as ancestor:
                ancestors.add(node)

        else:
            # Add previous node as ancestor:
            ancestors.add(breadcrumb[-1])

    def expression_hierarchy(self, expr: expression.Expression) -> list[int]:
        """Returns the position in hierarchy of the given expression as a list of immediate parents"""
        # Despite our concepts being usually Fully defined, we don't want to build descendants for them (yet)
        ancestral_nodes = set()

        # Find all ancestors starting from the root node
        self._check_concept_ancestorship(normal_form=expr.normal_form(self), node=SNOMED_ROOT,
                                         visited_nodes=set(), ancestors=ancestral_nodes)

        # Remove redundant ancestors
        clean_list = list(self.remove_redundant_parents(ancestral_nodes))

        return clean_list

    def get_relationship_groups(self, concept_id: int) -> list[data_model.RelationshipGroup]:
        return self.nodes[concept_id]['relationships']
