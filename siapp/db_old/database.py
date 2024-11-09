from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlmodel import Session, select
from siapp.db.models import Association, engine
from siapp.utils.retention_index import retention_index


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


def get_mean_response_time(association):
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
    return mean_single_response_time


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


def update_association(association):
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


##############################################################################
# Hour logging
from typing import Dict, List
from siapp.db.models import WorkDay, WorkLog, engine
from datetime import datetime, timedelta
from sqlmodel import Session, select
import polars as pl


def set_work_log(check_in: bool, time: datetime) -> None:
    if current_state() == check_in:
        return None
    with Session(engine) as session:
        # Check if there is a workday for today
        today = time
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        statement = select(WorkDay).where(WorkDay.date == today)
        work_day = session.exec(statement).first()
        if work_day is None:
            work_day = WorkDay(date=today)
            session.add(work_day)
            session.commit()
            session.refresh(work_day)
        work_log = WorkLog(timestamp=time, check_in=check_in)
        session.add(work_log)
        session.commit()
        session.refresh(work_log)
        work_day.worklog.append(work_log)
        session.add(work_day)
        session.refresh(work_day)
        session.commit()


def current_state() -> bool:
    with Session(engine) as session:
        statement = select(WorkLog)
        work_log = session.exec(statement).all()
        if work_log is None:
            return False
        log = None
        for log in work_log:
            pass
        if log is None:
            return False
        return log.check_in


def analyze_hours() -> None:
    with Session(engine) as session:
        statement = select(WorkDay)
        work_days = session.exec(statement).all()
        for work_day in work_days:
            time_of_work = timedelta(seconds=0)
            lunch_break = timedelta(seconds=0)
            work_break = timedelta(seconds=0)
            work_logs = work_day.worklog
            if len(work_logs) % 2 != 0:
                work_logs = work_logs[0:-1]
            for i in range(len(work_logs)):
                if i % 2 == 0:
                    time_of_work += (
                        work_logs[i + 1].timestamp - work_logs[i].timestamp
                    )
                    if i == 0:
                        continue
                    # If the timestamp is between 11:10 and 13:50, it is a lunch break
                    if (
                        work_logs[i].timestamp.hour >= 11
                        and work_logs[i].timestamp.hour <= 14
                    ):
                        lunch_break = (
                            work_logs[i].timestamp - work_logs[i - 1].timestamp
                        )
                    else:
                        work_break += (
                            work_logs[i].timestamp - work_logs[i - 1].timestamp
                        )
            work_day.time_of_work = time_of_work
            work_day.lunch_break = lunch_break
            work_day.work_break = work_break
            session.add(work_day)
            session.commit()


def get_data_summary() -> List[Dict]:
    with Session(engine) as session:
        statement = select(WorkDay)
        work_days = session.exec(statement).all()
        data = []
        for work_day in work_days:
            data.append(
                {
                    "date": str(work_day.date),
                    "work_time": str(work_day.time_of_work),
                    "lunch_break": str(work_day.lunch_break),
                    "work_break": str(work_day.work_break),
                }
            )
    return data


def get_in_out_data() -> List[Dict]:
    with Session(engine) as session:
        statement = select(WorkDay)
        work_days = session.exec(statement).all()
        data = []
        for work_day in work_days:
            l_inout = []
            for work_log in work_day.worklog:
                l_inout.append(str(work_log.timestamp))
            data.append({"date": work_day.date, "inout": l_inout})
    return data


def get_export_data() -> pl.DataFrame:
    with Session(engine) as session:
        statement = select(WorkDay)
        work_days = session.exec(statement).all()
        data = []
        for work_day in work_days:
            d_workday = {"Day": work_day.date}
            l_inout = []
            for i, work_log in enumerate(work_day.worklog):
                timestamp = work_log.timestamp
                timestamp = timestamp.strftime("%H:%M")
                if i % 2 == 0:
                    d_workday[f"in {i}"] = timestamp
                else:
                    d_workday[f"out {i}"] = timestamp
            d_workday["Work Time"] = work_day.time_of_work
            d_workday["Lunch Break"] = work_day.lunch_break
            d_workday["Pause"] = work_day.work_break
            data.append(d_workday)
        df = pl.DataFrame(data)
    return df


def save_exported_data(output_folder: Path):
    data = get_export_data()
    filename = Path(".") / "HoursLog.xlsx"
    # Delete the file if it exists
    if filename.exists():
        filename.unlink()
    data.write_excel(filename)
    output_folder = Path(output_folder)
    output_file = output_folder / filename.name
    if output_file.exists():
        output_file.unlink()
    filename.rename(output_folder / filename.name)
