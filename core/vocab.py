# Copyright 2022 Sciforce Ukraine. All rights reserved.
from __future__ import annotations

import pandas as pd

import core.expression
from core import ontology
from utils.constants import ENGLISH
from utils.constants import EXPRESSION_LANGUAGE
from utils.constants import JACKALOPE_SPACE
from utils.constants import MANUAL_SPACE
from utils.constants import VALID_DOMAINS
from utils.logger import jacka_logger
from typing import Iterable, Optional, Any
import abc
import copy
import datetime

VocabularyInsert = dict[str, list[dict[str, str | float | int | None]]]

# Logger also may be inherited by backend implementations
vocabulary_logger = jacka_logger.getChild('Vocabulary')


class OmopVocabulary(abc.ABC):
    logger = vocabulary_logger

    def __init__(self, *args, **kwargs):
        self._current_omop_code: int = self._last_omop_code()
        self._current_manual_id: int = self._last_id_in_range(range_start=MANUAL_SPACE)
        self._current_jackalope_id: int = self._last_id_in_range(range_start=JACKALOPE_SPACE[0],
                                                                 range_end=JACKALOPE_SPACE[1])
        self.sctid_replacements: list[tuple[int, int]] = []

    def next_omop_code(self) -> str:
        self._current_omop_code += 1
        return 'OMOP' + str(self._current_omop_code)

    def next_manual_id(self) -> int:
        self._current_manual_id += 1
        return self._current_manual_id

    def next_jackalope_id(self) -> int:
        self._current_jackalope_id += 1
        return self._current_jackalope_id

    def add_source_concept(
            self,
            concept_code: str,
            vocabulary_id: str,
            concept_name: str,
            domain_id: str,
            concept_class_id: str,
            synonyms: Optional[Iterable[str]] = None,
            language_id: int = ENGLISH,
            ) -> VocabularyInsert:
        # Assert domain_id correctness:
        assert domain_id in VALID_DOMAINS
        synonyms = synonyms or []

        # Generate new concept_id in manual space:
        concept_id = self.next_manual_id()

        inserts = dict()
        # Append:
        inserts['concept'] = [{
            'concept_id': concept_id,
            'concept_name': concept_name,
            'domain_id': domain_id,
            'vocabulary_id': vocabulary_id,
            'concept_class_id': concept_class_id,
            'concept_code': concept_code,
            'standard_concept': None,
            'valid_start_date': '19700101',
            'valid_end_date': '20991231',
            'invalid_reason': None
            }]

        inserts['concept_synonym'] = []
        for synonym in synonyms:
            # noinspection PyTypeChecker
            inserts['concept_synonym'].append({
                'concept_id': concept_id,
                'concept_synonym_name': synonym,
                'language_concept_id': language_id
                })

        return inserts

    def add_vocabulary(
            self,
            vid: str,
            version: str,
            reference: str,
            concept_id: Optional[int] = None,
            name: Optional[str] = None,
            ) -> VocabularyInsert:

        if concept_id is None:
            concept_id = self.next_manual_id()

        inserts = {
            'concept': [{
                'concept_id': concept_id,
                'concept_name': vid,
                'domain_id': 'Metadata',
                'vocabulary_id': 'Vocabulary',
                'concept_class_id': 'Vocabulary',
                'concept_code': 'OMOP generated',
                'standard_concept': None,
                'valid_start_date': '19700101',
                'valid_end_date': '20991231',
                'invalid_reason': None,
                }],

            'vocabulary': [{
                'vocabulary_id': vid,
                'vocabulary_name': name or vid,
                'vocabulary_version': version,
                'vocabulary_reference': reference,
                'vocabulary_concept_id': concept_id,
                }]
            }
        return inserts

    def ingest_expression(
            self,
            input_expression: core.expression.Expression,
            ont: ontology.Ontology,
            source_id: int = None,
            given_name: Optional[str] = None,
            vocabulary_id: str = 'Jackalope',
            report_parents: bool = True
            ) -> VocabularyInsert:
        """Prepares SNOMED expression to be ingested by writing DELTA files on disc
        @param input_expression: data_model.Expression object to be evaluated
        @param ont: ont.Ontology to evaluate against
        @param source_id: Optional concept_id of a source concept
        @param given_name: Optional custom name for the new synthetic conceept
        @param vocabulary_id: Custom vocabulary_id to be assigned. Must be already present in VOCABULARY table
        @param report_parents: Flag whether to log found parents to the concole.
        """

        inserts = dict()

        if given_name is None and source_id is not None:
            given_name = self._get_concept_attribute(source_id, 'concept_name')

        # Substitute the SCTID in the expression:
        expression = copy.copy(input_expression)
        for old_sctid, new_sctid in self.sctid_replacements:
            expression.substitute_sctid(old_sctid, new_sctid)

        # Process the expression, finding its parents and hash-fingerprinted CONCEPT_CODE
        try:
            expression_parents = ont.expression_hierarchy(expression)
            expression_id: int = self.next_jackalope_id()
            expression_fingerprint = expression.hash_concept_code(ont)
        except ontology.AccidentalEquivalency as e:
            # Return a mapping instead
            target_id, = self._find_concepts(vocabulary_id=["SNOMED"], concept_code=[str(e.sctid)])

            self.sctid_replacements.append((expression.concept_id, e.sctid))
            return self.map_to(source_id, target_id)

        # If the fingerprint matches an existing concept, return a mapping instead
        existing_concept = self._find_concepts(vocabulary_id=[vocabulary_id], concept_code=[expression_fingerprint])
        if existing_concept:
            target_id, = existing_concept
            return self.map_to(source_id, target_id)

        # Using PCE in CONCEPT_NAME may look ugly, but is clean
        expression_name = given_name or expression.canonical(ont)
        if len(expression_name) > 255:
            expression_name = expression_name[:252] + '...'

        # Remember substituted concept_id for dependent expressions
        self.sctid_replacements.append((expression.concept_id, expression_id))

        # Get a slice of CONCEPT containing parent data
        query = {
            'vocabulary_id': ['SNOMED'],
            'concept_code': [str(p) for p in expression_parents]
            }
        parents_concepts: pd.DataFrame = self.query_table('concept', **query)

        remapped = []
        # replace non-standard parents
        for _, parent_row in parents_concepts[parents_concepts["standard_concept"].isnull()].iterrows():
            for target in self.get_mapping(parent_row['concept_id']):
                remapped.append(self.query_table('concept', concept_id=[target]))
        parents_concepts = pd.concat(
            (*remapped, parents_concepts[~parents_concepts["standard_concept"].isnull()])).drop_duplicates()

        if report_parents:
            self.logger.info("Found parents:")
            self.logger.info(parents_concepts.loc[:,
                             ["concept_id", "concept_code", "concept_name", "vocabulary_id", "standard_concept"]])

        # Pick domain among multiple parents from list of preference
        expression_domain = VALID_DOMAINS[min(VALID_DOMAINS.index(d) for d in parents_concepts['domain_id'])]

        # Take first concept class: it's not as relevant
        expression_class = parents_concepts.loc[0, 'concept_class_id']

        # Work on the inserts:
        insert_shared = {
            'valid_start_date': '19700101',
            'valid_end_date': '20991231',
            'invalid_reason': None
            }
        #  - CONCEPT
        inserts['concept'] = [{
            'concept_id': expression_id,
            'concept_name': expression_name,
            'domain_id': expression_domain,
            'vocabulary_id': vocabulary_id,
            'concept_class_id': expression_class,
            'concept_code': expression_fingerprint,
            'standard_concept': 'S',
            **insert_shared
            }]

        #  - CONCEPT_RELATIONSHIP
        #  -- 'Is a' to discovered parents
        inserts['concept_relationship'] = list()

        for parent_id in parents_concepts['concept_id']:
            insert_isa = {
                'concept_id_1': expression_id,
                'concept_id_2': parent_id,
                'relationship_id': 'Is a',
                **insert_shared
                }

            insert_subsumes = {
                'concept_id_1': parent_id,
                'concept_id_2': expression_id,
                'relationship_id': 'Subsumes',
                **insert_shared
                }

            inserts['concept_relationship'].append(insert_isa)  # type: ignore
            inserts['concept_relationship'].append(insert_subsumes)  # type: ignore

        #  -- Attribute relationships to attributes: LATER.
        pass  # TODO(@Eduard) After symposium, probably

        #  -- 'Maps to'
        #  --- self
        for rel_id in ('Maps to', 'Mapped from'):
            inserts['concept_relationship'].append(dict(
                concept_id_1=expression_id,
                concept_id_2=expression_id,
                relationship_id=rel_id,
                **insert_shared
                ))

        #  --- Source concept
        if source_id is not None:
            inserts['concept_relationship'].append(dict(
                concept_id_1=source_id,
                concept_id_2=expression_id,
                relationship_id='Maps to',
                **insert_shared
                ))

            inserts['concept_relationship'].append(dict(
                concept_id_1=expression_id,
                concept_id_2=source_id,
                relationship_id='Mapped from',
                **insert_shared
                ))

        # - CONCEPT_ANCESTOR
        # Get slice of the dataframe that contains every parent's ancestors
        parent_slice = self.query_table('concept_ancestor',
                                        descendant_concept_id=parents_concepts['concept_id'].to_list())

        # Modify levels of separation
        parent_slice.loc[:, 'min_levels_of_separation'] += 1
        parent_slice.loc[:, 'max_levels_of_separation'] += 1

        # Replace descendant
        parent_slice['descendant_concept_id'] = expression_id

        # Remove dublicates
        parent_slice = (parent_slice
                        .groupby(['ancestor_concept_id', 'descendant_concept_id'])
                        .agg({'min_levels_of_separation': 'min', 'max_levels_of_separation': 'max'})
                        .reset_index()
                        .rename({'min': 'min_levels_of_separation', 'max': 'max_levels_of_separation'}, axis=1)
                        )

        inserts['concept_ancestor'] = [row.to_dict(into=dict) for _, row in parent_slice.iterrows()]

        # Add quasiancestor link to self
        ancestor_self: dict = dict(
            ancestor_concept_id=expression_id,
            descendant_concept_id=expression_id,
            min_levels_of_separation=0,
            max_levels_of_separation=0
            )
        inserts['concept_ancestor'].append(ancestor_self)

        # Add normalized & raw canonical forms as synonyms to source and synthetic concepts
        raw, normal = expression.canonical(ont, raw=True), expression.canonical(ont, raw=False)
        ids = [expression_id] if source_id is None else [expression_id, source_id]
        inserts["concept_synonym"] = []
        for expr in {raw, normal}:
            for c_id in ids:
                if len(expr) <= 1000:  # convention field length limit
                    # noinspection PyTypeChecker
                    inserts["concept_synonym"].append({
                            'concept_id': c_id,
                            'concept_synonym_name': expr,
                            'language_concept_id': EXPRESSION_LANGUAGE,
                        })
        return inserts

    def map_to(self, source_id: int, target_id: int, follow_mapping: bool = True) -> VocabularyInsert:
        if follow_mapping:
            new_target_ids = self.get_mapping(target_id)
            # Prevent endless recursion:
            mapping_dicts = [self.map_to(source_id, new_target, follow_mapping=False) for new_target in new_target_ids]
            return self.join_inserts(*mapping_dicts)

        insert_shared = {
            'valid_start_date': '19700101',
            'valid_end_date': '20991231',
            'invalid_reason': None
            }

        out = {"concept_relationship": [
            {
                'concept_id_1': source_id,
                'concept_id_2': target_id,
                'relationship_id': 'Maps to',
                **insert_shared
                },
            {
                'concept_id_1': target_id,
                'concept_id_2': source_id,
                'relationship_id': 'Mapped from',
                **insert_shared
                }
            ]}
        return out

    def snomed_us_date(self) -> datetime.date:
        us_version_string = self._snomed_version_string().split(sep='; ')[1][:10]  # US version is listed 2nd
        return datetime.datetime.strptime(us_version_string, '%Y-%m-%d').date()

    @staticmethod
    def join_inserts(*inserts) -> VocabularyInsert:
        out = dict()

        for vi in inserts:
            for key, val in vi.items():
                if key in out:
                    out[key].extend(val)
                else:
                    out[key] = list(val)

        # Remove dublicates(sets can not contain dicts)
        new_out = dict()
        for key, val in out.items():
            new_out[key] = list()
            for d in val:
                if d not in new_out[key]:
                    new_out[key].append(d)
        return new_out

    @abc.abstractmethod
    def _find_concepts(self, **conditions) -> list[int]:
        """Return id of the concepts fullfiling conditions passed as {column name: iterable of allowed values}"""
        ...

    @abc.abstractmethod
    def query_table(self, tablename: str, **conditions) -> pd.DataFrame:
        """Return slice of table as pandas.Dataframe where rows fullfil conditions as
        {column name: iterable of allowed values}"""
        ...

    @abc.abstractmethod
    def _get_concept_attribute(self, concept_id: int, attribute: str) -> Any:
        """Return attribute of a concept with a certain concept_id"""
        ...

    @abc.abstractmethod
    def execute_inserts(self, inserts_dict: VocabularyInsert) -> None:
        """Insert changes into database provided as {table name: list of rows{column: value}"""
        ...

    @abc.abstractmethod
    def _last_omop_code(self) -> int:
        """Get index of the last OMOP[0-9]+ like code in the database."""
        ...

    @abc.abstractmethod
    def _last_id_in_range(self, range_start: Optional[int] = 0, range_end: Optional[int] = None) -> int:
        """Get the last occupied CONCEPT_ID in range. Defaults to range start if no concepts exist in the range."""
        ...

    @abc.abstractmethod
    def _snomed_version_string(self) -> str:
        ...

    @abc.abstractmethod
    def get_mapping(self, source_id) -> list[int]:
        ...

    def close_connection(self) -> None:
        """May be overriden by SQL implementations to close connection to the database."""
        ...

    def __del__(self):
        self.close_connection()

    @abc.abstractmethod
    def unmap(self, source_id) -> bool:
        """Remove all mappings and standard status from source_id. Return True if any changes were made."""
        ...

    @abc.abstractmethod
    def _set_concept_atrr(self, concept_id: int, attribute: str, value: Any) -> None:
        """Set attribute of a concept with a certain concept_id"""
        ...

    @abc.abstractmethod
    def drop_vocabulary(self, vocabulary_id) -> None:
        """Drop all concepts belonging to the vocabulary"""
        ...
