from __future__ import annotations

import os
import pickle
from typing import Iterable, Any

import core.data_model
import core.ontology
import core.vocab

import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'


class OmopVocabularyCSV(core.vocab.OmopVocabulary):
    logger = core.vocab.vocabulary_logger.getChild('CSV')
    """Reads OMOP Vocabulary data from disk, and writes changes in %table_name%_DELTA.csv files."""

    concept: pd.DataFrame
    concept_relationship: pd.DataFrame
    concept_ancestor: pd.DataFrame
    concept_synonym: pd.DataFrame
    vocabulary: pd.DataFrame

    _CSV_OPTIONS: dict = {
            'sep': ',',
            'line_terminator': '"',
            }

    def __init__(self, path: str,
                 source_concept_id: Iterable[int] | None = None) -> None:

        # Remember path to write down delta:
        self._path = path

        self.logger.info("Loading OMOP Source from CSV files...")
        source_concept_id = source_concept_id or []
        # Load all the relevant dataframes, keep only the relevant information
        self.logger.info('Loading CONCEPT...')
        self.concept = pd.read_csv(
                os.path.join(path, 'CONCEPT.csv'),
                sep='\t',
                low_memory=False
                )

        self.concept = self.concept.loc[
            self.concept['concept_id'].isin(source_concept_id) |
            (self.concept['vocabulary_id'] == 'SNOMED')
            ]
        self.logger.info('Loading CONCEPT_RELATIONSHIP...')
        self.concept_relationship = pd.read_csv(
                os.path.join(path, 'CONCEPT_RELATIONSHIP.csv'), sep='\t')
        self.concept_relationship = self.concept_relationship.loc[
            self.concept_relationship['concept_id_1'].isin(self.concept['concept_id']) &
            self.concept_relationship['concept_id_2'].isin(self.concept['concept_id'])
            ]

        self.logger.info('Loading CONCEPT_ANCESTOR...')
        self.concept_ancestor = pd.read_csv(os.path.join(
                path, 'CONCEPT_ANCESTOR.csv'), sep='\t', dtype=np.int64)

        self.concept_ancestor = self.concept_ancestor.loc[
            self.concept_ancestor["descendant_concept_id"].isin(self.concept['concept_id']) &
            self.concept_ancestor["ancestor_concept_id"].isin(self.concept['concept_id'])
            ]

        self.logger.info('Loading CONCEPT_SYNONYM...')
        self.concept_synonym = pd.read_csv(os.path.join(path, 'CONCEPT_SYNONYM.csv'), sep='\t')
        self.concept_synonym = self.concept_synonym.loc[
            self.concept_synonym['concept_id'].isin(self.concept['concept_id'])
            ]

        self.vocabulary = pd.read_csv(os.path.join(path, 'VOCABULARY.csv'), sep='\t')

        # Conversion for concept_id replacements for nested expressions
        self.sctid_replacements = list()

        super(OmopVocabularyCSV, self).__init__(path, source_concept_id)

    def execute_inserts(self, inserts_dict: core.vocab.VocabularyInsert) -> None:

        # Execute inserts to tables in memory:
        for key, values in inserts_dict.items():
            df = getattr(self, key)
            frames = [df]
            for dct in values:
                frame = pd.DataFrame([dct])
                frames.append(frame)
            new_df = pd.concat(frames, ignore_index=True)
            setattr(self, key, new_df)

            # Write down (or append) DELTA tables on disc
            output_path = os.path.join(self._path, key.upper()) + '_DELTA.csv'
            df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), **self._CSV_OPTIONS)
            # It's up to user to manage and merge these tables, as we expect them to be further fed to an SQL database

    def dump(self, filepath: str):

        if not filepath[-4].lower().endswith('.omp'):
            filepath += '.omp'

        with open(filepath, 'wb') as f:
            self.logger.info(f"Dumping cache to {filepath}...")
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath) -> core.vocab.OmopVocabulary:

        with open(filepath, 'rb') as f:
            loaded = pickle.load(f)
            cls.logger.info(f"Loaded {cls} object containing "
                            f"{len(loaded.concept)} concept entries.")

            return loaded

    def _get_concept_attribute(self, concept_id: int, attribute: str):
        return (self.concept
                .loc[self.concept['concept_id'] == concept_id]
                .loc[:, attribute]
                .iloc[0])

    def _find_concepts(self, **conditions: dict[str, Iterable[Any]]) -> list[int]:
        idx = pd.DataFrame({k: self.concept[k].isin(v) for k, v in conditions.items()}).all(axis=1)
        return self.concept.loc[idx, 'concept_id'].to_list()

    def query_table(self, tablename: str, **conditions) -> pd.DataFrame:
        frame = getattr(self, tablename)
        idx = pd.DataFrame({k: frame[k].isin(v) for k, v in conditions.items()}).all(axis=1)
        return frame[idx]

    def _last_omop_code(self) -> int:
        # Find the maximum existing OMOP\d+ code:
        concept_codes = (self.concept['concept_code']
                         .loc[self.concept['concept_code']
                         .str.match(f'^OMOP\\d+$').fillna(value=False)])
        return (concept_codes
                .str.removeprefix('OMOP')
                .astype(np.int64)
                .max())

    def _last_id_in_range(self, range_start: int = 0, range_end: int | None = None) -> int:
        if range_end is not None:
            idx = self.concept['concept_id'].between(range_start, range_end, inclusive='left')
        else:
            idx = self.concept['concept_id'] >= range_start

        if idx.any():
            return self.concept['concept_id'][idx].min()

        return range_start

    def _snomed_version_string(self) -> str:
        return self.vocabulary.loc[self.vocabulary['vocabulary_id'] == 'SNOMED', 'vocabulary_version'].iloc[0]

    def get_mapping(self, source_id) -> list[int]:
        row_idx = ((self.concept_relationship['relationship_id'] == 'Maps to') &
                   (self.concept_relationship['concept_id_1'] == source_id))
        return self.concept_relationship[row_idx, 'concept_id_2'].to_list()

    def unmap(self, source_id) -> bool:
        self.logger.warning("Not implemented for CSV backend.")
        return False

    def _set_concept_atrr(self, concept_id: int, attribute: str, value: Any) -> None:
        concept_attributes = self.concept.loc[self.concept['concept_id'] == concept_id].iloc[0, :].to_dict()
        concept_attributes[attribute] = value
        insert: core.vocab.VocabularyInsert = {'concept': [concept_attributes]}
        self.execute_inserts(insert)

    def drop_vocabulary(self, vocabulary_id) -> None:
        self.logger.warning("Not implemented for CSV backend.")
