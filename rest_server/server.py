from __future__ import annotations

import datetime
import json
import sys
from datetime import datetime

from flask import Flask
from flask import jsonify
from flask import request
from flask_pydantic import validate

from core import expression_process
from core import ontology
from core import vocab
from rest_server import request_model
from utils.constants import HASH_COMPATIBILITY_VERSION
from utils.constants import JACKALOPE_HOST
from utils.constants import JACKALOPE_VERSION
from utils.constants import JACKALOPORT
from utils.logger import jacka_logger
from vocab_backend import csv_backend
from vocab_backend import sql_backend

server_logger = jacka_logger.getChild('RESTServer')
app = Flask('Jackalope')


def get_instance() -> JackalopeREST | None:
    return JackalopeREST.instance


class JackalopeREST:
    instance: JackalopeREST | None = None
    ont_version: datetime.date
    voc_version: datetime.date
    ont: ontology.Ontology
    voc: vocab.OmopVocabulary

    def __new__(cls, **kwargs):
        """Singleton pattern. Only overwrite singleton instance if new set of kwargs is provided."""
        if cls.instance is None or kwargs:
            cls.instance = super().__new__(cls)
            cls.instance._init(**kwargs)
            return cls.instance
        else:
            return cls.instance

    def _init(self, **kwargs):
        self.rebuild_omop = kwargs.get('rebuild_omop', True)
        self.backend = kwargs.get('backend', 'sql')
        self.snomed_path = kwargs.get('snomed_path', None)
        self.vocabs_path = kwargs.get('vocabs_path', None)
        self.pickled_ont_path = kwargs.get('pickle_ont', None)
        self.host = kwargs.get('host', JACKALOPE_HOST)
        self.port = kwargs.get('port', JACKALOPORT)
        self.sql_connection_options = kwargs.get('connection_properties', None)

    def startup(self):
        server_logger.info(f"Starting up Jackalope REST server version {JACKALOPE_VERSION}.")

        self._load_ontology()

        server_logger.info(f"Connecting to {self.backend.upper()} backend.")
        self._connect_backend()
        server_logger.info("Done.")

        server_logger.info("Checking SNOMED US versions in both databases.")
        self.compare_versions()

        self.voc.execute_inserts(self.voc.add_vocabulary(
                vid='Jackalope',
                version=JACKALOPE_VERSION,
                reference='https://sciforce.solutions/industries/medtech',
                concept_id=self.voc.next_jackalope_id()
                ))

        sys.stdout.write("SERVER ONLINE")
        server_logger.info("Jackalope is running. Make sure to wear stovepipes.")
        server_logger.info(f"API is available at http://{JACKALOPE_HOST}:{JACKALOPORT}/jackalope/v1.0/")

    def compare_versions(self):
        server_logger.info("Checking SNOMED US versions in both databases.")
        self.ont_version = self.ont.version["SNOMED CT US"]
        server_logger.debug(f"SNOMED US appears to be dated {self.ont_version} in RF2 source")
        self.voc_version = self.voc.snomed_us_date()
        server_logger.debug(f"SNOMED US appears to be dated {self.voc_version} in OMOP Vocabulary")
        if self.ont_version != self.voc_version:
            server_logger.warning("WARNING: It is recommended to download corresponding version of SNOMED US edition. "
                                  "Things WILL break.")
        else:
            server_logger.info("SNOMED US versions match.")

    def _connect_backend(self):
        if self.backend == 'csv':
            if self.rebuild_omop:
                self.voc = csv_backend.OmopVocabularyCSV(self.vocabs_path)
                self.voc.dump("vocabs")  # type: ignore
            else:
                self.voc = csv_backend.OmopVocabularyCSV.load("vocabs.omp")
        elif self.backend == "sql":
            with open(self.sql_connection_options) as f:
                sql_connection_options = json.load(f)
                self.voc = sql_backend.OmopVocabularySQL(**sql_connection_options, clean=self.rebuild_omop)
        else:
            raise ValueError(f"{self.backend} is not a known backend option.")

    def _load_ontology(self):
        if self.pickled_ont_path is not None:
            server_logger.debug("Pickle file provided. Loading from pickle. Ignoring SNOMED path.")
            server_logger.info("Unpickling saved SNOMED Ontology.")
            try:
                self.ont = ontology.Ontology.load(self.pickled_ont_path)
                return
            except FileNotFoundError:
                server_logger.warning("Specified Pickle file not found!")

        server_logger.info("Loading SNOMED Ontology from source RF2 files.")
        self.ont = ontology.Ontology.build(self.snomed_path)
        self.ont.populate(dump_filename="SNOMED")

        server_logger.info("Done.")


@app.route('/jackalope/v1.0/get/version', methods=['GET'])
@validate()
def version():
    if request.method == 'GET':
        return request_model.Version(
                app=JACKALOPE_VERSION,
                hasher=str(HASH_COMPATIBILITY_VERSION),
                snomed_omop=str(get_instance().voc_version),
                snomed_rf2=str(get_instance().ont_version)
            )


@app.route('/jackalope/v1.0/get/concept_info', methods=['GET'])
@validate(query=request_model.GetConcept)
def concept_info():
    if request.method == 'GET':
        concept_id = request.args['concept_id']
        concept = (get_instance().voc.query_table('concept', concept_id=[concept_id])
                   .iloc[0]
                   .to_dict())
        return request_model.ConceptInfo(concept_data=concept)


@app.route('/jackalope/v1.0/add/vocabulary', methods=['POST'])
@validate(body=request_model.AddVocabularyRequest)
def add_vocab():
    if request.method == 'POST':
        data = request.get_json()
        vocab_inserts = get_instance().voc.add_vocabulary(
                vid=data['vocabulary_id'],
                name=data['vocabulary_name'],
                reference=data['vocabulary_reference'],
                version=data['vocabulary_version'],
            )
        get_instance().voc.execute_inserts(vocab_inserts)
        return jsonify({})


@app.route('/jackalope/v1.0/add/source_concept', methods=['POST'])
@validate(body=request_model.AddSourceConceptRequest)
def add_source_concept():
    if request.method == 'POST':
        data = request.get_json()
        concept_insert = get_instance().voc.add_source_concept(
                concept_code=data['concept_code'],
                concept_name=data['concept_name'],
                vocabulary_id=data['vocabulary_id'],
                concept_class_id=data['concept_class_id'],
                domain_id=data['domain_id'],
                synonyms=data.get('synonyms', None),
            )
        get_instance().voc.execute_inserts(concept_insert)

        return request_model.ConceptId(concept_id=concept_insert['concept'][0]['concept_id'])


@app.route('/jackalope/v1.0/add/pce', methods=['POST'])
@validate(body=request_model.AddPCERequest)
def add_post_coordinated_expression():
    if request.method == 'POST':
        data = request.get_json()

        # Test if the expression is valid
        pass

        # Deserialize the expression
        pce_processor = expression_process.Processor()
        pce = pce_processor.process(data['post_coordinated_expression'])[0]

        expression_insert = get_instance().voc.ingest_expression(
                pce,
                get_instance().ont,
                source_id=data['source_id'],
                given_name=data.get('given_name', None)
                )
        get_instance().voc.execute_inserts(expression_insert)

        response = {
                'concept_id': None,
                'concept_code': None,
                'parent_concepts': None,
                'mapped_concepts': None,
            }
        if 'concept' in expression_insert:
            response['concept_id'] = expression_insert['concept'][0]['concept_id']
            response['concept_code'] = expression_insert['concept'][0]['concept_code']

        # Add references to found parent or mapped concepts
        if 'concept_relationship' in expression_insert:
            response['parent_concepts'] = []
            response['mapped_concepts'] = []
            for cr in expression_insert['concept_relationship']:
                if cr['relationship_id'] == 'Maps to':
                    response['mapped_concept'] = cr['concept_id_2']
                elif cr['relationship_id'] == 'Is a':
                    response['parent_concepts'].append(cr['concept_id_2'])
        return request_model.AddPCEResponse(**response)


@app.route('/jackalope/v1.0/delete/mapping', methods=['DELETE'])
@validate(query=request_model.GetConcept)
def unmap_concept():
    if request.method == 'DELETE':
        concept_id = request.args['concept_id']
        changes = get_instance().voc.unmap(concept_id)
        return request_model.BoolResponse(changes_made=changes)


@app.route('/jackalope/v1.0/delete/vocabulary', methods=['DELETE'])
@validate(query=request_model.VocabId)
def delete_vocabulary():
    if request.method == 'DELETE':
        vid = request.args['vocabulary_id']
        get_instance().voc.drop_vocabulary(vid)
        return jsonify({})


def start_server(**kwargs):
    jack = JackalopeREST(**kwargs)
    jack.startup()
    try:
        app.run(host=jack.host, port=jack.port)
    finally:
        server_logger.info("Shutting down.")
        jack.voc.close_connection()
        server_logger.info("Goodbye.")


def main():
    with open('config.json') as f:
        DEFAULT_ARGS = json.load(f)

    start_server(**DEFAULT_ARGS)


if __name__ == '__main__':
    main()
