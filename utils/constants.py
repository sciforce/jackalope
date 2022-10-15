# Copyright 2022 Sciforce Ukraine. All rights reserved.
import pathlib
import json

# Hashing constants
HASH_COMPATIBILITY_VERSION = b'1ALPHA'
OMOP_CODE_FIELD_LENGTH = 50

# Server constants
with open(pathlib.Path().cwd() / 'config.json', 'r') as f:
    _DEFAULT_ARGS = json.load(f)
    JACKALOPE_HOST, JACKALOPORT = _DEFAULT_ARGS['host'], _DEFAULT_ARGS['port']
JACKALOPE_VERSION = '0.4-ALPHA'

# SNOMED constants
SNOMED_ROOT = 138875005
SNOMED_ROOT_MODULE = 900000000000012004
SCT_MODEL_COMPONENT = 900000000000012004
SNOMED_US_MODULE = 731000124108
DEFINED = 900000000000073002
FSN = 900000000000003001
ISA = 116680003

# OMOP constants
ENGLISH = 4180186
EXPRESSION_LANGUAGE = 45768546  # Placeholder, needs an OMOP Extension concept
JACKALOPE_SPACE = 1_000_000_000, 2_000_000_000
MANUAL_SPACE = 2_000_000_000
ID_RANGE = 9
VALID_DOMAINS = ['Procedure', 'Measurement', 'Condition', 'Context-dependent',
                 'Observation', 'Metadata']  # SNOMED should not be used for Drug, even if attributes are good
