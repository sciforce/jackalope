# Copyright 2022 Sciforce Ukraine. All rights reserved.
import requests
import pathlib
import pandas as pd
from utils.logger import jacka_logger
from utils.constants import JACKALOPE_HOST
from utils.constants import JACKALOPORT

_client_logger = jacka_logger.getChild('RESTClient')
_client_logger.counter = 0


class RequestError(Exception):
    def __init__(self, code: int, server_message: str | None = None):
        self.code = code
        self.message = server_message or f"Request failed with code {code}"


def _test_200_ok(response: requests.Response) -> None:
    if response.status_code != 200:
        raise RequestError(response.status_code, response.json().get('error', None))


def _new_concept_logger():
    logger = _client_logger.getChild(str(_client_logger.counter))
    _client_logger.counter += 1
    return logger


def add_vocabulary(vid, version, reference, name, host=JACKALOPE_HOST, port=JACKALOPORT) -> None:
    response = requests.post(
            f'http://{host}:{port}/jackalope/v1.0/add/vocabulary',
            json={
                "vocabulary_id": vid,
                "vocabulary_version": version,
                "vocabulary_reference": reference,
                "vocabulary_name": name,
                }
        )
    _test_200_ok(response)


def add_source_concept(
        concept_code,
        vocabulary_id,
        concept_name,
        domain_id,
        concept_class_id,
        synonyms,
        host=JACKALOPE_HOST,
        port=JACKALOPORT
        ) -> int:

    response = requests.post(
            f'http://{host}:{port}/jackalope/v1.0/add/source_concept',
            json={
                "concept_code": concept_code,
                "vocabulary_id": vocabulary_id,
                "concept_name": concept_name,
                "domain_id": domain_id,
                "concept_class_id": concept_class_id,
                "synonyms": synonyms,
                }
            )
    _test_200_ok(response)
    return response.json()['concept_id']


def add_expression(
        post_coordination_expression,
        concept_id,
        host=JACKALOPE_HOST,
        port=JACKALOPORT
        ) -> dict:
    response = requests.post(
            f'http://{host}:{port}/jackalope/v1.0/add/pce',
            json={
                "post_coordinated_expression": post_coordination_expression,
                "source_id": concept_id,
                }
            )
    _test_200_ok(response)
    return response.json()


def get_concept_info(concept_id, host=JACKALOPE_HOST, port=JACKALOPORT) -> pd.Series:
    response = requests.get(
            f'http://{host}:{port}/jackalope/v1.0/get/concept_info',
            params={'concept_id': concept_id}
            )
    _test_200_ok(response)
    return pd.Series(response.json()['concept_data'])


def unmap_concept(concept_id, host=JACKALOPE_HOST, port=JACKALOPORT) -> bool:
    response = requests.delete(
            f'http://{host}:{port}/jackalope/v1.0/delete/mapping',
            params={
                "concept_id": concept_id,
                }
            )
    _test_200_ok(response)
    return response.json()['changes_made']


def main(filename=pathlib.Path().absolute() / 'use_cases_icd.csv'):
    _client_logger.info("Adding SciForce vocabulary for examples.")
    add_vocabulary(
        vid='SciForce',
        name='SciForce',
        version='1.0',
        reference='https://sciforce.solutions/industries/medtech'
        )
    _client_logger.info('OK.')

    examples = pd.read_csv(filename)

    def _process_row(row: pd.Series):
        concept_logger = _new_concept_logger()
        concept_logger.debug('Assigned new logger')
        concept_logger.info(f"Processing {row['concept_code']} {row['concept_name']}")
        concept_logger.info(f"Expression: {row['post_coordination_expression']}")

        concept_id = add_source_concept(
            concept_code=row['concept_code'],
            vocabulary_id=row.get('vocabulary_id', 'SciForce'),
            concept_name=row['concept_name'],
            domain_id='Condition',
            concept_class_id='ICD10 code',
            synonyms=[]
            )

        concept_logger.info(f"Added concept with id {concept_id}")

        concept_logger.info('Trying removing previous mapping.')
        if unmap_concept(concept_id):
            concept_logger.info(f"Unmapped concept {concept_id}")
        else:
            concept_logger.info(f"Concept {concept_id} was not mapped.")

        eval_result = add_expression(
            post_coordination_expression=row['post_coordination_expression'],
            concept_id=concept_id
            )

        if 'concept_id' in eval_result and eval_result['concept_id'] is not None:
            concept_logger.info(f"New concept created: "
                                f"concept_id = {eval_result['concept_id']}, "
                                f"concept_code = '{eval_result['concept_code']}'")

        if 'mapped_concepts' in eval_result and eval_result['mapped_concepts']:
            concept_logger.info("Mapped to concepts:")
            for concept_id in eval_result['mapped_concepts']:
                mapping_target = get_concept_info(concept_id)
                concept_logger.info(f"* {mapping_target['concept_id']} "
                                    f"{mapping_target['concept_code']} "
                                    f"{mapping_target['concept_name']} "
                                    f"{mapping_target['vocabulary_id']}")

        if 'parent_concepts' in eval_result and eval_result['parent_concepts']:
            concept_logger.info("Parent concepts:")
            for concept_id in eval_result["parent_concepts"]:
                parent = get_concept_info(concept_id)
                concept_logger.info(f"* {parent['concept_id']} "
                                    f"{parent['concept_code']} "
                                    f"{parent['concept_name']} "
                                    f"{parent['vocabulary_id']}")

    for _, row_ in examples.iterrows():
        try:
            _process_row(row_)
        except RequestError as e:
            _client_logger.error(f"Request error: {e.code} {e.message}."
                                 f"Skipping {row_['concept_code']} {row_['concept_name']}")
    _client_logger.info("Done!")


if __name__ == '__main__':
    main()
