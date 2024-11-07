from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from db.models import Association, engine
from utils.retention_index import retention_index


def image_path_to_bytes(image_path: str) -> bytes:
    with open(image_path, "rb") as file:
        image_bytes = file.read()
    return image_bytes


def add_association(
    information: str,
    information_image: Optional[bytes] = None,
    character_text: Optional[str] = None,
    pao_image: Optional[bytes] = None,
    action_text: Optional[str] = None,
    object_text: Optional[str] = None,
):
    if information_image is not None:
        information_image = image_path_to_bytes(information_image)
    if pao_image is not None:
        pao_image = image_path_to_bytes(pao_image)

    with Session(engine) as session:
        association = Association(
            information_image=information_image,
            information=information,
            pao_image=pao_image,
            character_text=character_text,
            action_text=action_text,
            object_text=object_text,
            creation_date=datetime.now(),
        )
        session.add(association)
        session.commit()


def get_mean_response_time(association: Association):
    l_response_times = [
        association.last_response_time_I_to_PAO,
        association.last_response_time_P_to_I,
        association.last_response_time_A_to_I,
        association.last_response_time_O_to_I,
    ]
    # Remove the None values
    l_response_times = [x for x in l_response_times if x is not None]
    mean_single_response_time = None
    if l_response_times:
        mean_single_response_time = sum(l_response_times) / len(
            l_response_times
        )


def get_element_number():
    with Session(engine) as session:
        statements = select(Association)
        associations = session.exec(statements).all()
        return len(associations)


def calculate_retention_index():
    now = datetime.now()
    with Session(engine) as session:
        statements = select(Association)
        associations = session.exec(statements).all()
        # Found the mean response time for each direction
        l_mean_response_time = []
        for association in associations:
            if association.refresh_count > 0:
                mean_single_response_time = get_mean_response_time(association)
                if mean_single_response_time is not None:
                    l_mean_response_time.append(mean_single_response_time)

        # Calculate the mean response time for all associations
        mean_response_time = None
        if l_mean_response_time != []:
            mean_response_time = sum(l_mean_response_time) / len(
                l_mean_response_time
            )

        for association in associations:
            # Calculate retention index
            difficulty = association.difficulty
            if mean_response_time is not None:
                mean_time = get_mean_response_time(association)
                if mean_time is not None and mean_response_time != 0:
                    difficulty = mean_time / mean_response_time * difficulty
            if association.last_repetition_date is not None:
                association.retention_index = retention_index(
                    now - association.last_repetition_date,
                    association.refresh_count,
                    difficulty,
                )
            else:
                association.retention_index = 0
            session.add(association)
        session.commit()


def update_association(association: Association):
    with Session(engine) as session:
        # Load the association with the same id
        statement = select(Association).where(Association.id == association.id)
        association_db = session.exec(statement).first()
        # Update the association
        association_db.information = association.information
        association_db.information_image = association.information_image
        association_db.character_text = association.character_text
        association_db.pao_image = association.pao_image
        association_db.action_text = association.action_text
        association_db.object_text = association.object_text
        association_db.last_response_time_I_to_PAO = (
            association.last_response_time_I_to_PAO
        )
        association_db.last_response_time_P_to_I = (
            association.last_response_time_P_to_I
        )
        association_db.last_response_time_A_to_I = (
            association.last_response_time_A_to_I
        )
        association_db.last_response_time_O_to_I = (
            association.last_response_time_O_to_I
        )
        association_db.creation_date = association.creation_date
        association_db.last_repetition_date = association.last_repetition_date
        association_db.refresh_count = association.refresh_count
        association_db.difficulty = association.difficulty
        association_db.retention_index = association.retention_index
        # Commit the changes
        session.add(association_db)
        session.commit()


def get_associations(n_associations: int = 5):
    with Session(engine) as session:
        statements = select(Association).limit(n_associations)
        associations = session.exec(statements).all()
        return associations


def get_all_associations():
    with Session(engine) as session:
        statements = select(Association)
        associations = session.exec(statements).all()
        return associations
