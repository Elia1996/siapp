from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from db.models import Association, engine
from utils.retention_index import retention_index


def add_association(
    information: str,
    character_text: Optional[str] = None,
    action_text: Optional[str] = None,
    object_text: Optional[str] = None,
):
    with Session(engine) as session:
        association = Association(
            information=information,
            character_text=character_text,
            action_text=action_text,
            object_text=object_text,
            creation_date=datetime.now(),
        )
        session.add(association)
        session.commit()


def calculate_retention_index():

    now = datetime.now()
    with Session(engine) as session:
        statements = select(Association)
        associations = session.exec(statements).all()
        for association in associations:
            # Calculate retention index
            association.retention_index = retention_index(
                now - association.last_repetition_date,
                association.refresh_count,
                association.difficulty,
            )


def get_associations(n_associations: int = 5):
    with Session(engine) as session:
        statements = select(Association).limit(n_associations)
        associations = session.exec(statements).all()
        return associations
