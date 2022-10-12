import cProfile
import pathlib
import pstats
import sys
from core.logger import jacka_logger

PROFILING = False


def _main_fallback():
    import pandas as pd
    import json

    from core import ontology
    from core import expression_process
    from core import vocab
    from vocab_backend import csv_backend
    from vocab_backend import sql_backend

    # General options
    REBUILD_ONT = False
    REBUILD_OMOP = True
    BACKEND = 'sql'
    AUTOACCEPT = True

    SNOMED_PATH = "/snomed/Snapshot"
    VOCABS_PATH = "/Users/eduardkorchmar/git/Jackalope/omop_vocab"

    auto = AUTOACCEPT
    if REBUILD_ONT:
        ont = ontology.Ontology.build(SNOMED_PATH)
        ont.populate(dump_filename="SNOMED")
    else:
        ont = ontology.Ontology.load('SNOMED.ont')

    if BACKEND == 'csv':
        if REBUILD_OMOP:
            voc = csv_backend.OmopVocabularyCSV(VOCABS_PATH)
            voc.dump('vocabs')
        else:
            voc = csv_backend.OmopVocabularyCSV.load('vocabs.omp')
    elif BACKEND == 'sql':
        with open('/Users/eduardkorchmar/git/Jackalope/connection_properties.json', 'r') as f:
            eng = json.load(f)
        voc = sql_backend.OmopVocabularySQL(**eng, clean=REBUILD_OMOP, permanent_connection=True)
    else:
        raise ValueError(f"{BACKEND} is not a known backend option.")

    # Compare versions
    ont_version = ont.version['SNOMED CT US']
    voc_version = voc.snomed_us_date()
    print(f'SNOMED US appears to be dated {ont_version} in RF2 source, OMOP Vocabulary contains version {voc_version}')
    if ont_version != voc_version:
        print("WARNING: It is recommended to download corresponding version of SNOMED US edition. Things will break.")

    examples = pd.read_csv('use_cases_icd.csv')

    voc.execute_inserts(voc.add_vocabulary(
        vid='Jackalope',
        version='0.2-ALPHA',
        reference='https://sciforce.solutions/industries/medtech',
        concept_id=voc.next_jackalope_id()
        ))

    voc.execute_inserts(voc.add_vocabulary(
        vid='SciForce',
        version='1.0',
        reference='https://sciforce.solutions/industries/medtech'
        ))

    for _, example in examples.iterrows():
        print(40 * '-')
        print(f"Processing {example['concept_code']} {example['concept_name']}")
        print(40 * '-')
        print(f"Expression: {example['post_coordination_expression']}")

        processor = expression_process.Processor()
        expr = processor.process(example["post_coordination_expression"])[0]

        # Add the source concept
        source_insert = voc.add_source_concept(concept_code=example['concept_code'],
                                               vocabulary_id=example['vocabulary_id'],
                                               concept_name=example['concept_name'],
                                               domain_id='Condition',
                                               concept_class_id='ICD10 code',
                                               synonyms=[])

        # Source insert
        print("Inserts for the source concept:")
        for target, insert in source_insert.items():
            if not insert:
                continue
            print(f"{target.upper()}:")
            print(pd.DataFrame(insert))
        voc.execute_inserts(source_insert)

        # Expression insert
        print("Finding parents and preparing inserts...")

        source_id: int = source_insert['concept'][0]['concept_id']
        expression_insert: vocab.VocabularyInsert = voc.ingest_expression(expr, ont, source_id=source_id)
        for target, insert in expression_insert.items():
            if not insert:
                continue
            print(f"{target.upper()}:")
            print(pd.DataFrame(insert))

        if auto:
            execute = True
            print("Automatically accepting all changes!")
        else:
            print("Accept changes? [Y]es/[n]o/accept [a]ll")
            answer = input().lower()
            if not answer or answer[0] == 'y':
                execute = True
                print("Accepting.")
            elif answer[0] == 'a':
                execute = auto = True
                print("Automatically accepting all changes!")
            else:
                execute = False
                print("Skipping.")

        if execute:
            voc.execute_inserts(expression_insert)

    voc.close_connection()


def _main():
    from rest_client import client
    import subprocess
    from time import sleep

    # If filename is provided, start the server & client
    if len(sys.argv) > 1:
        server = subprocess.Popen(
                ['python3', 'rest_server/server.py'],
                stdout=subprocess.PIPE,
                cwd=pathlib.Path().absolute())
        while True:
            stdout_line = server.stdout.readline().decode('utf-8')
            if stdout_line.startswith('SERVER ONLINE'):
                break
            # We use print instead of logging: it is raw Flask output
            print(stdout_line, end='')
        sleep(1)

        try:
            client.main(pathlib.Path(sys.argv[1]).absolute())
        finally:
            server.kill()
    else:
        # Otherwise start the server only and respond to requests
        import rest_server.server
        rest_server.server.main()


if __name__ == '__main__':
    ROUTINE = _main
    jacka_logger.info(f"Starting Jackalope, profiling: {PROFILING}")
    if PROFILING:
        with cProfile.Profile(builtins=False) as prof:
            ROUTINE()
        stats = pstats.Stats(prof)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats('stats.prof')
    else:
        ROUTINE()

    jacka_logger.info("Jackalope finished.")
