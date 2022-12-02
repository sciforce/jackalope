# Copyright 2022 Sciforce Ukraine. All rights reserved.
from typing import Optional
from pydantic import BaseModel
import datetime


class Version(BaseModel):
    app: str
    hasher: str
    snomed_omop: str
    snomed_rf2: str


class GetConcept(BaseModel):
    concept_id: int


class ConceptInfo(BaseModel):
    concept_data: dict[str, str | int | datetime.date | None]


class AddVocabularyRequest(BaseModel):
    vocabulary_id: str
    vocabulary_name: str
    vocabulary_reference: str
    vocabulary_version: str


class AddSourceConceptRequest(BaseModel):
    concept_code: str
    concept_name: str
    domain_id: str
    vocabulary_id: str
    concept_class_id: str
    synonyms: Optional[list[str]] = None


class AddPCERequest(BaseModel):
    post_coordinated_expression: str
    source_id: int


class ConceptId(BaseModel):
    concept_id: int


class AddPCEResponse(BaseModel):
    concept_id: Optional[int]
    concept_code: Optional[str]
    parent_concepts: Optional[list[int]]
    mapped_concepts: Optional[list[int]]


class BoolResponse(BaseModel):
    changes_made: bool


class VocabId(BaseModel):
    vocabulary_id: str


class ValidationErrorResponse(BaseModel):
    error: str
    expression: str
    rule: str


class OMOPTableInserts(BaseModel):
    inserts: dict[str, list[dict[str, str | int | float | datetime.date | None]]]
