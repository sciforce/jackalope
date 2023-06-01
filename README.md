# Introduction
You are looking at **Jackalope**, the open-source tool for enabling 
support for SNOMED CT-style post-coordinated expressions during ETL 
conversion of source EMR data into OMOP CDM format. Jackalope is developed
and supported by Sciforce for the benefit of open science and the OHDSI community.

Scroll to the bottom of the document for API reference.

### Read more:
* [Sciforce](https://sciforce.solutions/industries/medtech)
* [OHDSI](https://www.ohdsi.org/)
* [Jackalope showcase](https://www.ohdsi.org/2022showcase-41/)

# Background
SNOMED CT is a large, complex, and highly structured ontology. It also 
features a syntax for expressing complex clinical using post-coordinated 
expressions, meaning coordinated use of multiple SNOMED CT concepts to 
represent a single complex idea.

The OMOP Common Data Model (CDM) is a standard for representing observational
clinical data, also featuring a rich ecosystem of tools for research. SNOMED CT
forms a centerpiece of the CDM, being used as the primary Standard coding system 
for many concept Domains. 

However, the CDM does not support the use of SNOMED CT post-coordinated 
expressions. Or, rather, it used to not support them, until the Jackalope 
came along. Now, it is possible to build custom standard representation for any
source concept by representing it as a SNOMED CT post-coordinated expression. 
Jackalope will build an extension of SNOMED CT hierarchy inside a deployed OMOP CDM 
instance, allowing for full use of OMOP CDM tools.


### Read more:
* [Post-coordinated expression syntax](https://www.snomed.org/news-and-events/articles/snomed-ct-compositional-grammar-specification)
* [Classical OMOP ETL process](https://ohdsi.github.io/TheBookOfOhdsi/ExtractTransformLoad.html#step-2-create-the-code-mappings)

# Setup
## Prerequisites
Jackalope is written in Python 3.10. It requires an installed Python interpreter and ANTLR4 
runtime to run. It is recommended to use a virtual environment for running Jackalope. All 
required dependencies are listed in `requirements.txt` file.

Jackalope also requires source RF2 files for SNOMED CT. Using matching version of SNOMED CT US
is strongly recommended for compatibility, but not enforced. Check the `VOCABULARY.VOCAULARY_VERSION`
for `vocabulary_id = 'SNOMED'` in your OMOP CDM instance to find out which version of SNOMED CT US to download.

Jackalope can be run on any system and device, but having at least 8 Gb of free RAM is recommended.
For installation, simply download or clone the repository and run `pip install -r requirements.txt`.

### Read more:
* [Python 3.10](https://www.python.org/downloads/)
* [venv](https://docs.python.org/3/library/venv.html)
* [ANTLR4 runtime](https://www.antlr.org/download.html)
* [SNOMED CT US *Archive*](https://www.nlm.nih.gov/healthit/snomedct/archive.html)

## Backend setup
Jackalope is abstracted from backend database through `SQLAlchemy` library, 
allowing for easy integration with any SQL-compatible database. Currently, PostgreSQL 
and sqlite3 have been tested as backends, but no SQL code generated is platform-specific.

To connect to a database, you need to create a configuration file `connection_properties.json` in 
JSON format. Use `connection_properties.json.example` as a template.


| Field name     | Description                                                                                                                                         | Optional |
|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| "protocol"     | Database protocol as specified by SQLAlchemy. Currently, only "postgresql" and "sqlite" are tested, but all are supported.                          | No       |
| "ssh_address"  | Address of the SSH tunnel to use for connecting to the database. Leave empty if not using SSH tunnel.                                               | Yes      |
| "ssh_port"     | Port of the SSH tunnel to use for connecting to the database. Leave empty if not using SSH tunnel.                                                  | Yes      |
| "ssh_username" | Username for the SSH tunnel to use for connecting to the database. Leave empty if not using SSH tunnel.                                             | Yes      |
| "ssh_password" | Password for the SSH tunnel to use for connecting to the database. If not specified, but other ssh fields are present, will be prompted in `stdin`. | Yes      |
| "db_address"   | Address of the database to connect to. Localhost is accepted.                                                                                       | No       |
| "db_port"      | Port of the database to connect to. 5432 is default for Postgres.                                                                                   | No       |
| "db_user"      | Username for the database to connect to.                                                                                                            | No       |
| "db_password"  | Password for the database to connect to. If not specified, attempt to connect will be made without password.                                        | Yes      |
| "db_name"      | Name of the database to connect to.                                                                                                                 | No       |


**WARNING**: Jackalope will make changes to the database.

Jackalope has also a fallback option to work directly with Athena downloaded CSV files. In this case,
changes will be represented as _DELTA.csv files, which can be used to update the database manually.

### Read more:
* [SQLAlchemy supported engines](https://docs.sqlalchemy.org/en/14/core/engines.html)
* [Athena CSV files](https://athena.ohdsi.org/)

## Jackalope setup

Jackalope is a server architecture application, which can be run in a terminal or as a background process. 
It has a sepparate configuration file `config.json` in JSON format. It should be good enough in default state
for the most usecases.

Its fields are:
 * `host` - port to run the server on. Default is localhost.
 * `port` - port to run the server on. Default is 52252.
 * `snomed_path` - relative or absolute path to the SNOMED CT US RF2 files. Default is `snomed`.
 * `vocabs_path` - relative or absolute path to the vocabulary files. Default is `omop_vocab`. Will only be used in `csv` backend.
 * `backend` - backend to use. Can be `csv` or `sql`. Default is `sql`.
 * `pickle_ont` - path where to store (and look for) the binary file of cached SNOMED Ontology.
 * `connection_properties` - path to the connection properties file. Default is `connection_properties.json`.
 * `rebuild_omop` - whether to reset **all** custom concepts in the OMOP CDM instance on connect. Default is `false`.
 * `stateless` - whether to run the server in stateless mode. Default is `false`. When set to `true`, will  not make any changes to the database,
and instead output the changes in JSON format to `stdout`. This is useful for open use web-service implementation. Important:
all `concept_id` and `concept_code` will be set to 0 or `null` in this mode, except for hash-generated. This option is ignored if
filename is passed as a command line argument.

On the first run, Jackalope will pickle SNOMED CT ontology file for faster loading.
 
## Running Jackalope
Jackalope can be run in two ways:
 * As a tool which will evaluate expressions from a single CSV file and exit.
 * As a background service, responding to REST API requests.

### Running as a tool
To run Jackalope as a tool, run `$ python main.py %FILENAME%` in the root directory of the repository.
This will evaluate all expressions in the file and load the changes to the database.

`%FILENAME%` must be a path to a UTF-8 encoded, comma-delimited, .CSV file. Example file can be found
in `use_cases_icd.csv` in the root directory of the repository.

File should have thefollowing structure:

| Column name                 | Description                                                                                                 | Optional |
|-----------------------------|-------------------------------------------------------------------------------------------------------------|----------|
| vocabulary_id               | Vocabulary ID of the source concept. Defaults to "SciForce". **Must** have an entry present in `VOCABULARY` | Yes      |
| concept_code                | Concept code of the source concept.                                                                         | No       |
| concept_name                | Concept name of the source concept. Will also be used for the new standard concept                          | No       |
| concept_class_id            | Concept class ID of the source concept. Defaults to "Clinical Finding"                                      | Yes      |
| domain_id                   | Domain ID of the source concept. Defaults to "Condition". For concept set purposes will not matter.         | Yes      |
| post_coordinated_expression | Post-coordinated expression to be evaluated. Must be in Compositional Grammar syntax*                       | No       |

*-Subexpressions are not currently supported.

Found parents and changes to the database will be printed to the console during the run.

### Running as a service

To run Jackalope as a service, run `$ python main.py` in the root directory of the repository.
This will start a server on the specified port and host, which will respond to REST API requests.
The server is not intended as a full replacement for an SQL client, and can only make changes in 
line with the post-coordinated expression evaluation. `rest_client/client.py` can be referred to as
an example of how to use the API.

# API Specification
Default endpoint is http://localhost:52252/jackalope/v1.0/

## GET 
### get/version/
Returns the version of the server, concept_code hasher, and SNOMED US in both RF2 and database backend.
```json
{
    "app": "0.2-ALPHA",
    "hasher": "1ALPHA",
    "snomed_omop": "2021-09-01",
    "snomed_rf2": "2021-09-01"
}
```

### get/concept_info?concept_id=`%CONCEPT_ID%`
Returns information about a concept in the database having unique id equal to `%CONCEPT_ID%`. 
This is a convenience tool, it does not provide information about relationships, synonyms or hierarchy. 
```json
{
    "concept_id": 123456,
    "concept_code": "123456789",
    "concept_name": "Some concept",
    "vocabulary_id": "SNOMED",
    "domain_id": "Condition",
    "concept_class_id": "Clinical Finding",
    "standard_concept": "S"
}
```

## POST
### add/vocabulary/
Requires a data package in JSON format. Adds a new custom vocabulary to the database. 
Must be run prior to adding new concept to said vocabulary. 
```json
{
    "vocabulary_id": "SciForce",
    "vocabulary_name": "SciForce Ukraine",
    "vocabulary_reference": "https://sciforce.solutions/industries/medtech",
    "vocabulary_version": "2021-09-01"
}
```

### add/source_concept
Requires a data package in JSON format. Adds a new source non-standard concept to the database.
```json
{
    "concept_code": "123456789",
    "concept_name": "Some concept",
    "vocabulary_id": "SciForce",
    "concept_class_id": "Clinical Finding",
    "domain_id": "Condition"
}
```

Returns a data package in JSON format. Contains the concept_id of the newly created concept.
Value of concept_id will be in conventionally designated "manual" space (>2,000,000,000).
```json
{
    "concept_id": 2123456789
}
```

### add/pce
Requires a data package in JSON format. 
Evaluates a post-coordinated expressions, and adds relevant changes affecting the source concept.
**Will not deprecate or overwrite existing relations**
```json
{
    "source_id": 2123456789,
    "post_coordinated_expression": "74580009: {405816004 =  25723000, 260686004 = 129404003}"
}
```

Returns a data package in JSON format describing changes in the database.

#### Option 1: Mapped to an existing concept(s) or previously evaluated expression
```json
{
    "mapped_concepts": [123456]
}
```

#### Option 2: Mapped to a new synthetic concept inside SNOMED hierarchy
Assigns concept_id in designated "synthetic" space 
(1,000,000,000<concept_id<2,000,000,000). Not yet an established convention. Any number of
matching parents can be created.
```json
{
    "parent_concepts": [123456, 78910, 11121314],
    "concept_id": 123456789,
    "concept_code": "e7bc867c5d56acdf0fa0ff4b291d85137c375142234f580a68"
}
```

The value of concept_code is 25-bit BLAKE2b hash of the cannonical normal form of the post-coordinated expression.
It is guaranteed to be shared with all semantically synonymous expressions.

## DELETE
### delete/mapping?concept_id=`%CONCEPT_ID%`

Removes all mapping relationships, `CONCEPT_ANCESTOR` entries and contents of `STANDARD_CONCEPT` field for the concept.
Returns a boolean value indicating if any changes were made. It is recommended to access
this endpoint before building a new mapping for the concept, as it is not done automatically.
```json
{
  "changes_made": true
}
```

### delete/vocabulary?vocabulary_id=`%VOCABULARY_ID%`
Removes all entries in all tables related to the vocabulary. Returns empty JSON object.