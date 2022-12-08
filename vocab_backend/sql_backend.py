from __future__ import annotations

from getpass import getpass
from typing import Type, TypeVar, Any

import sqlalchemy as sa
import sshtunnel
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect
import core.vocab

import pandas as pd

import utils.constants

_LOCALHOST = '127.0.0.1'

_OMOP_metadata = sa.MetaData()
_Base = declarative_base(metadata=_OMOP_metadata)
_omr_concept = TypeVar("_omr_concept", bound=_Base)


def _get_ssh_pass() -> str:
    return getpass(prompt=f"Password for SSH (hidden):")


def get_mapper_class(tablename: str) -> Type[_omr_concept]:
    """Returns the class associated with the table name"""
    for cls in _Base.__subclasses__():
        if cls.__tablename__ == tablename:
            return cls
    raise ValueError(f'No mapper class found for tablename {tablename:!r}.')


class ForwardedEngine:
    """Creates a SQLAlchemy engine that forwards a local port to a remote port."""

    def __init__(
            self,
            protocol: str,
            db_user: str,
            db_password: str,
            db_address: str,
            db_port: int,
            db_name: str,
            ssh_address: str | None = None,
            ssh_port: int | None = None,
            ssh_username: str | None = None,
            ssh_password: str | None = None,
            metadata: sa.MetaData = _OMOP_metadata,
            resolve_metadata: bool = False,
            permanent_connection: bool = False,
            ) -> None:
        self._db_address = db_address, db_port
        self._resolve_metadata = resolve_metadata

        if ssh_password is None and ssh_address is not None:
            ssh_password = _get_ssh_pass()

        if ssh_address is not None:
            self.ssh_forwarder = sshtunnel.SSHTunnelForwarder(
                    ssh_username=ssh_username,
                    ssh_password=ssh_password,
                    ssh_host=(ssh_address, ssh_port),
                    remote_bind_address=self._db_address
                    )
        else:
            self.ssh_forwarder = None

        # Deter creation of engine until port is open
        self.engine = None
        self.metadata: sa.MetaData = metadata
        self._session: Session | None = None

        self._url_template = (f"{protocol}://"f"{db_user}{':'+db_password if db_password else ''}@"
                              "{ip}:{port}"  # Will be replaced with address
                              f"/{db_name}")

        # If permanent connection is requested, open it now
        self.permanent_connection = permanent_connection
        if self.permanent_connection:
            self._session = self.__enter__(resolve_metadata=self._resolve_metadata)

    def __enter__(self, resolve_metadata: bool = False) -> Session:
        if self.permanent_connection and self._session is not None:
            self._session.execute('SET CONSTRAINTS ALL DEFERRED;')
            return self._session

        if self.ssh_forwarder is not None:
            self.ssh_forwarder.start()
            self.engine = sa.create_engine(self._url_template.format(
                    ip=_LOCALHOST,
                    port=str(self.ssh_forwarder.local_bind_port),
                    ))
        else:
            self.engine = sa.create_engine(self._url_template.format(
                    ip=self._db_address[0], port=self._db_address[1],
                    ))

        self.metadata.bind = self.engine

        # If metadata resolution is pending, execute it
        if self._resolve_metadata:
            self.metadata.create_all()
            self._resolve_metadata = False

        self._session = Session(self.engine)
        return self._session

    def __exit__(self, exception_type, *_) -> None:
        if self.permanent_connection:
            # Don't close permanent connection
            self._session.commit()
            return

        if self._session is not None:

            if exception_type is None:
                self._session.commit()
            self._session.close()

        if self.ssh_forwarder is not None:
            self.ssh_forwarder.stop()


# Data tables
class Concept(_Base):
    __tablename__ = "concept"
    concept_id = sa.Column(sa.Integer, primary_key=True)
    concept_name = sa.Column('concept_name', sa.String(255))
    domain_id = sa.Column(sa.String(20),
                          sa.ForeignKey("domain.domain_id"))
    vocabulary_id = sa.Column(sa.String(20),
                              sa.ForeignKey("vocabulary.vocabulary_id"))
    concept_class_id = sa.Column(
            sa.String(20),
            sa.ForeignKey("concept_class.concept_class_id")
            )
    standard_concept = sa.Column('standard_concept', sa.String(1), nullable=True)
    concept_code = sa.Column('concept_code', sa.String(50))
    valid_start_date = sa.Column(sa.Date)
    valid_end_date = sa.Column(sa.Date)
    invalid_reason = sa.Column(sa.String(1), nullable=True)

    def __repr__(self) -> str:
        return (f"{self.concept_id}\t{self.concept_code}\t"
                f"{self.concept_name}")


# Work around lack of PK in concept_synonym by making all fields PK
class ConceptSynonym(_Base):
    __tablename__ = 'concept_synonym'
    concept_id = sa.Column(sa.Integer,
                           sa.ForeignKey("concept.concept_id"), primary_key=True)
    concept_synonym_name = sa.Column(sa.String(1000), primary_key=True)
    language_concept_id = sa.Column(sa.Integer,
                                    sa.ForeignKey("concept.concept_id"),
                                    primary_key=True)

    def __repr__(self) -> str:
        return (f"Synonym ({self.concept_synonym_name} of "
                f"{self.concept_id})")


# Metadata
class Vocabulary(_Base):
    __tablename__ = 'vocabulary'
    vocabulary_id = sa.Column(sa.String(20), primary_key=True)
    vocabulary_name = sa.Column(sa.String(255))
    vocabulary_reference = sa.Column(sa.String(255))
    vocabulary_version = sa.Column(sa.String(255))
    vocabulary_concept_id = sa.Column(sa.Integer,
                                      sa.ForeignKey("concept.concept_id", deferrable=True))

    def __repr__(self) -> str:
        return (f"Vocabulary (id={self.vocabulary_id}, "
                f"version={self.vocabulary_version})")


class Domain(_Base):
    __tablename__ = "domain"
    domain_id = sa.Column(sa.String(20), primary_key=True)
    domain_name = sa.Column(sa.String(255))
    domain_concept_id = sa.Column(sa.Integer,
                                  sa.ForeignKey("concept.concept_id", deferrable=True))

    def __repr__(self) -> str:
        return f"Domain (id={self.domain_id}"


class ConceptClass(_Base):
    __tablename__ = "concept_class"
    concept_class_id = sa.Column(sa.String(20), primary_key=True)
    concept_class_name = sa.Column(sa.String(255))
    concept_class_concept_id = sa.Column(sa.Integer,
                                         sa.ForeignKey("concept.concept_id", deferrable=True))

    def __repr__(self) -> str:
        return f"ConceptClass (id={self.concept_class_id}"


class Relationship(_Base):
    __tablename__ = "relationship"
    relationship_id = sa.Column(sa.String(20), primary_key=True)
    relationship_name = sa.Column(sa.String(255))
    is_hierarchical = sa.Column(sa.String(1))
    defines_ancestry = sa.Column(sa.String(1))
    reverse_relationship_id = sa.Column(sa.String(20))
    relationship_concept_id = sa.Column(sa.Integer,
                                        sa.ForeignKey("concept.concept_id", deferrable=True))

    def __repr__(self) -> str:
        return f"Relationship (id={self.relationship_id}"

    # Concept relationships


class ConceptRelationship(_Base):
    __tablename__ = "concept_relationship"
    concept_id_1 = sa.Column(sa.Integer,
                             sa.ForeignKey("concept.concept_id"),
                             primary_key=True)
    concept_id_2 = sa.Column(sa.Integer,
                             sa.ForeignKey("concept.concept_id"),
                             primary_key=True)
    relationship_id = sa.Column(sa.String(20),
                                sa.ForeignKey("relationship.relationship_id"))
    valid_start_date = sa.Column(sa.Date)
    valid_end_date = sa.Column(sa.Date)
    invalid_reason = sa.Column(sa.String(1), nullable=True)

    def __repr__(self) -> str:
        return (f"Relationship ({self.concept_id_1} - "
                f"{self.relationship_id} - "
                f"{self.concept_id_2})")


class ConceptAncestor(_Base):
    __tablename__ = "concept_ancestor"
    ancestor_concept_id = sa.Column(sa.Integer,
                                    sa.ForeignKey("concept.concept_id"),
                                    primary_key=True)
    descendant_concept_id = sa.Column(sa.Integer,
                                      sa.ForeignKey("concept.concept_id"),
                                      primary_key=True)
    min_levels_of_separation = sa.Column(sa.Integer)
    max_levels_of_separation = sa.Column(sa.Integer)

    def __repr__(self) -> str:
        return (f"ConceptAncestor ({self.ancestor_concept_id} subsumes "
                f"{self.descendant_concept_id})")


class DrugStrength(_Base):
    __tablename__ = "drug_strength"
    drug_concept_id = sa.Column(sa.Integer,
                                sa.ForeignKey("concept.concept_id"),
                                primary_key=True)
    ingredient_concept_id = sa.Column(sa.Integer,
                                      sa.ForeignKey("concept.concept_id"),
                                      primary_key=True)
    amount_value = sa.Column(sa.Numeric, nullable=True)
    amount_unit_concept_id = sa.Column(sa.Integer,
                                       sa.ForeignKey("concept.concept_id"),
                                       nullable=True)
    numerator_value = sa.Column(sa.Numeric, nullable=True)
    numerator_unit_concept_id = sa.Column(sa.Integer,
                                          sa.ForeignKey("concept.concept_id"),
                                          nullable=True)
    denominator_value = sa.Column(sa.Numeric, nullable=True)
    denominator_unit_concept_id = sa.Column(
            sa.Integer,
            sa.ForeignKey("concept.concept_id"),
            nullable=True,
            )
    box_size = sa.Column(sa.Integer, nullable=True)
    valid_start_date = sa.Column(sa.Date)
    valid_end_date = sa.Column(sa.Date)
    invalid_reason = sa.Column(sa.String(1), nullable=True)

    def __repr__(self) -> str:
        return (f"DrugStrength ({self.drug_concept_id} contains "
                f"{self.ingredient_concept_id})")


class PackContent(_Base):
    __tablename__ = "pack_content"
    pack_concept_id = sa.Column(sa.Integer,
                                sa.ForeignKey("concept.concept_id"),
                                primary_key=True)
    drug_concept_id = sa.Column(sa.Integer,
                                sa.ForeignKey("concept.concept_id"),
                                primary_key=True)
    amount = sa.Column(sa.Integer, nullable=True)
    box_size = sa.Column(sa.Integer, nullable=True)

    def __repr__(self) -> str:
        return (f"PackContent ({self.pack_concept_id} contains "
                f"{self.drug_concept_id})")


# Add additional relationships after all classses are defined.
# CONCEPT
Concept.domain = relationship("Domain", foreign_keys='Concept.domain_id')
Concept.concept_class = relationship("ConceptClass",
                                     foreign_keys='Concept.concept_class_id')
Concept.vocabulary = relationship("Vocabulary",
                                  foreign_keys='Concept.vocabulary_id')

# External details
Concept.relationship_objects = relationship(
        "Concept",
        secondary="concept_relationship",
        primaryjoin="concept.c.concept_id == concept_relationship.c.concept_id_1",
        secondaryjoin="concept.c.concept_id == concept_relationship.c.concept_id_2",
        backref="Concept.relationship_subjects",
        )
Concept.relationship_subjects = relationship(
        "Concept",
        secondary="concept_relationship",
        primaryjoin="concept.c.concept_id == concept_relationship.c.concept_id_2",
        secondaryjoin="concept.c.concept_id == concept_relationship.c.concept_id_1",
        backref="Concept.relationship_objects",
        )
Concept.descendants = relationship(
        "Concept",
        secondary="concept_ancestor",
        primaryjoin="concept.c.concept_id == concept_ancestor.c.ancestor_concept_id",
        secondaryjoin="concept.c.concept_id == concept_ancestor.c.descendant_concept_id",
        backref="Concept.ancestors",
        )
Concept.ancestors = relationship(
        "Concept",
        secondary="concept_ancestor",
        primaryjoin="concept.c.concept_id == concept_ancestor.c.descendant_concept_id",
        secondaryjoin="concept.c.concept_id == concept_ancestor.c.ancestor_concept_id",
        backref="Concept.descendants",
        )

# CONCEPT_SYNONYM
ConceptSynonym.language = relationship(
        "Concept",
        foreign_keys='ConceptSynonym.language_concept_id')


class OmopVocabularySQL(core.vocab.OmopVocabulary):
    """SQL-Alchemy powered backend to read and write changes to SQL-hosted OMOP database."""

    _stored_engine: ForwardedEngine | None = None
    logger = core.vocab.vocabulary_logger.getChild('SQL')

    def __init__(self, clean: bool = True, **engine_options) -> None:
        # Remember engine options:
        self.engine_options = engine_options

        # Ask for SSH password in advance and
        if 'ssh_address' in self.engine_options and 'ssh_password' not in self.engine_options:
            self.engine_options['ssh_password'] = _get_ssh_pass()  # type: ignore

        # Create a static engine if specified:
        if engine_options.get('permanent_connection', False):
            self._stored_engine = self.start_session(resolve_metadata=engine_options.get('resolve_metadata', None))

        # test connection:
        self.logger.info("Ensuring remote table metadata aligns with the model...")
        with self.start_session(resolve_metadata=True):
            self.logger.info(f"{self} initialized successfully.")

        if clean is True:
            self.logger.info(f"Removing previously generated entries...")
            self.cleanup()
            self.logger.info("Cleanup complete.")

        super(OmopVocabularySQL, self).__init__(clean, **engine_options)

    def start_session(self, resolve_metadata: bool = False) -> ForwardedEngine:
        if self._stored_engine is not None:
            return self._stored_engine
        return ForwardedEngine(**self.engine_options, resolve_metadata=resolve_metadata)

    def _find_concepts(self, **conditions) -> list[int]:
        stmt = sa.select(Concept.concept_id)
        # Iteratively add refinements to the statement
        for column, values in conditions.items():
            stmt = stmt.where(getattr(Concept, column).in_(values))

        with self.start_session() as session:
            return [concept['concept_id'] for concept in session.execute(stmt).fetchall()]

    def query_table(self, tablename: str, **conditions) -> pd.DataFrame:
        mapper_class_table = get_mapper_class(tablename).__table__
        stmt = sa.select(mapper_class_table)
        # Iteratively add refinements to the statement
        for column, values in conditions.items():
            stmt = stmt.where(getattr(mapper_class_table.c, column).in_(values))

        with self.start_session() as session:
            result = session.execute(stmt)
            return pd.DataFrame(result.fetchall())

    def _get_concept_attribute(self, concept_id: int, attribute: str):
        column = getattr(Concept, attribute)
        stmt = sa.select(column).where(Concept.concept_id == concept_id)
        with self.start_session() as session:
            return session.execute(stmt).fetchone()[attribute]

    def execute_inserts(self, inserts_dict: core.vocab.VocabularyInsert) -> None:
        """Loads existing content if it matches, deletes it; then, performs insert.
        Since we are only expected to work with the local instance of CDM, we do not manage deprecation."""
        with self.start_session() as session:
            with session.no_autoflush:
                # Work around circular foreign keys
                session.execute('SET CONSTRAINTS ALL DEFERRED')
                for tablename, inserts in inserts_dict.items():

                    table_class = get_mapper_class(tablename)
                    primary_keys = inspect(table_class).primary_key

                    for insert in inserts:
                        # Delete existing rows matching inserts on primary key
                        condition = {pk.name: insert[pk.name] for pk in primary_keys}
                        deletable_row_stmt = sa.delete(table_class)
                        for col, val in condition.items():
                            deletable_row_stmt = deletable_row_stmt.where(getattr(table_class, col) == val)
                        session.execute(deletable_row_stmt)

                        # Perform insert
                        new = table_class(**insert)
                        session.add(new)
                session.commit()

    def cleanup(self) -> None:
        """Removes all custom and generated concepts and other entries"""
        affected_classes = {
                ConceptAncestor: ['descendant_concept_id', 'ancestor_concept_id'],
                ConceptSynonym: ['concept_id'],
                ConceptRelationship: ['concept_id_1', 'concept_id_2'],
                Vocabulary: ['vocabulary_concept_id'],
                Concept: ['concept_id'],  # Important to be the last to go
                }

        with self.start_session() as session:
            with session.no_autoflush:
                # Work around circular foreign keys
                session.execute('SET CONSTRAINTS ALL DEFERRED;')
                for cls, cid_keys in affected_classes.items():
                    deleted_rows = 0
                    for key in cid_keys:
                        field = getattr(cls, key)
                        delete_rows_q = (sa.delete(cls).where(sa.or_(
                                sa.and_(
                                        field >= utils.constants.JACKALOPE_SPACE[0],
                                        field < utils.constants.JACKALOPE_SPACE[1]),
                                field > utils.constants.MANUAL_SPACE)))
                        try:
                            deleted = session.execute(delete_rows_q)
                            deleted_rows += deleted.rowcount
                        except sa.exc.IntegrityError:
                            self.logger.error(f"Could not delete rows from {cls.__tablename__} due to foreign key "
                                              f"constraints. Consider setting all foreign keys deferrable.")

                            # We still raise, because inserts will break if we don't clean up properly.
                            raise
                    self.logger.debug(f"Deleted {deleted_rows} from {cls.__tablename__}...")

    def _last_omop_code(self) -> int:
        subquery = (sa.select(Concept
                              .concept_code
                              .regexp_replace("^OMOP", "")
                              .cast(sa.Integer)
                              .label('int_code')
                              ).where(Concept.concept_code.regexp_match("^OMOP\\d+$")))
        query = sa.select(sa.func.max(subquery.c.int_code))
        with self.start_session() as session:
            return session.execute(query).fetchone()[0]

    def _last_id_in_range(self, range_start: int = 0, range_end: int | None = None) -> int:
        query = sa.select(Concept.concept_id).order_by(Concept.concept_id).limit(1)
        if range_end is not None:
            query = query.where(Concept.concept_id.between(range_start, range_end - 1))
        else:
            query = query.where(Concept.concept_id >= range_start)

        with self.start_session() as session:
            result = session.execute(query)
            try:
                return result.fetchone()[0]
            except TypeError:
                return range_start

    def _snomed_version_string(self) -> str:
        return self.query_table('vocabulary', vocabulary_id=['SNOMED']).loc[:, "vocabulary_version"].iloc[0]

    def get_mapping(self, source_id) -> list[int]:
        return (self
                .query_table('concept_relationship', concept_id_1=[source_id], relationship_id=['Maps to'])
                .loc[:, 'concept_id_2']
                .to_list()
                )

    def close_connection(self) -> None:
        if self._stored_engine is not None:
            self.logger.info("Closing database connection.")
            self._stored_engine.permanent_connection = False
            self._stored_engine.__exit__(None)

    def unmap(self, concept_id) -> bool:
        changes = False
        statements = []

        # Remove standard status if present
        if self._get_concept_attribute(concept_id, 'standard_concept') in ('S', 'C'):
            self._set_concept_atrr(concept_id, 'standard_concept', None)
            changes = True

            # Remove concept_ancestor entries
            if changes:
                delete_stmt = sa.delete(ConceptAncestor).where(
                        sa.or_(ConceptAncestor.descendant_concept_id == concept_id,
                               ConceptAncestor.ancestor_concept_id == concept_id))
                statements.append(delete_stmt)

        # Remove Maps to and Mapped from relationships
        delete_stmt = sa.delete(ConceptRelationship).where(
                sa.and_(
                        sa.or_(
                                ConceptRelationship.concept_id_1 == concept_id,
                                ConceptRelationship.concept_id_2 == concept_id
                            ),
                        ConceptRelationship.relationship_id.in_(['Maps to', 'Mapped from'])
                        )
                )
        statements.append(delete_stmt)

        with self.start_session() as session:
            for delete in statements:
                deleted = session.execute(delete)
                if deleted.rowcount > 0:
                    changes = True
        return changes

    def _set_concept_atrr(self, concept_id: int, attribute: str, value: Any):
        column = getattr(Concept, attribute.lower())
        stmt = sa.update(Concept).where(Concept.concept_id == concept_id).values({column: value})
        with self.start_session() as session:
            session.execute(stmt)
            session.commit()

    def drop_vocabulary(self, vocabulary_id) -> None:
        # List all concepts belonging to the vocabulary
        doomed_concept_ids = self._find_concepts(vocabulary_id=[vocabulary_id])
        vocabulary_concept_id = self.query_table('vocabulary',
                                                 vocabulary_id=[vocabulary_id]).loc[:, 'vocabulary_concept_id'].iloc[0]
        doomed_concept_ids.append(vocabulary_concept_id)

        self.logger.info(f"Queuing {len(doomed_concept_ids)} concepts related to '{vocabulary_id}' for deletion.")

        affected_classes = {
                ConceptAncestor: ['descendant_concept_id', 'ancestor_concept_id'],
                ConceptSynonym: ['concept_id'],
                ConceptRelationship: ['concept_id_1', 'concept_id_2'],
                Vocabulary: ['vocabulary_concept_id'],
                Concept: ['concept_id'],  # Important to be the last to go
                }

        with self.start_session() as session:
            with session.no_autoflush:
                # Work around circular foreign keys
                session.execute('SET CONSTRAINTS ALL DEFERRED;')
                for cls, cid_keys in affected_classes.items():
                    deleted_rows = 0
                    for key in cid_keys:
                        field = getattr(cls, key)
                        delete_rows_q = (sa.delete(cls).where(field.in_(doomed_concept_ids)))
                        deleted = session.execute(delete_rows_q)
                        deleted_rows += deleted.rowcount
                    self.logger.debug(f"Deleted {deleted_rows} from {cls.__tablename__}...")

        self.logger.info(f"Deleted '{vocabulary_id}'.")
