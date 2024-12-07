from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple
import sqlite3
from siapp.db.models import Association
import csv
from kivy.utils import platform
import os
from siapp.utils.retention_index import retention_index


def image_path_to_bytes(image_path: str) -> bytes:
    with open(image_path, "rb") as file:
        return file.read()


def can_write_to_directory(path):
    test_file = os.path.join(path, "temp_test_file.tmp")
    try:
        # Try creating a temporary file to test write access
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(
            test_file
        )  # Clean up the test file if it was created successfully
        return True
    except (IOError, OSError):
        # If an error occurs, write access is likely restricted
        return False


def get_fmanager_path() -> str:
    # Try different paths to open the file manger in an existing directory
    print("Platform:", platform)
    import os

    if platform == "android":
        from android.storage import primary_external_storage_path

        storage_base_path = primary_external_storage_path()
        storage_path = os.path.join(storage_base_path, "Documents")
        if os.path.exists(storage_path) and can_write_to_directory(
            storage_path
        ):
            print("Opening in:", storage_path)
            return storage_path
        if os.path.exists(storage_base_path) and can_write_to_directory(
            storage_base_path
        ):
            print("Opening in:", storage_base_path)
            return storage_base_path
        storage_path = "/storage/emulated/0"
        if os.path.exists(storage_path) and can_write_to_directory(
            storage_path
        ):
            print("Opening in:", storage_path)
            return storage_path
    print("Opening in:", os.path.expanduser("~"))
    return "/"


def add_association(
    information: str,
    information_image: Optional[str] = None,
    character_text: Optional[str] = None,
    pao_image: Optional[str] = None,
    action_text: Optional[str] = None,
    object_text: Optional[str] = None,
):
    from siapp.db.models import DATABASE
    from shutil import copyfile
    from pathlib import Path

    # Copy the image near the database
    if information_image and os.path.exists(information_image):
        info = Path(information_image)
        new_info = Path(DATABASE).parent.absolute() / info.name
        print(
            "Copying", information_image, "to", new_info, "database:", DATABASE
        )
        copyfile(information_image, new_info)
        information_image = str(new_info)
    if pao_image and os.path.exists(pao_image):
        pao = Path(pao_image)
        new_pao = Path(DATABASE).parent.absolute() / pao.name
        copyfile(pao_image, new_pao)
        pao_image = str(new_pao)

    print("Adding association to: ", DATABASE)
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Print all associations

        cursor.execute(
            """
            INSERT INTO Association (
                information, information_image, character_text, pao_image, 
                action_text, object_text, creation_date, refresh_count, difficulty, 
                retention_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
        """,
            (
                information,
                information_image,
                character_text,
                pao_image,
                action_text,
                object_text,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()


def get_element_number() -> int:
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Association")
        return cursor.fetchone()[0]


def get_mean_response_time(assoc: Association) -> Tuple[Optional[float], int]:
    association_id = assoc.id
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT last_response_time_I_to_PAO, last_response_time_P_to_I, 
                   last_response_time_A_to_I, last_response_time_O_to_I
            FROM Association WHERE id=?
        """,
            (association_id,),
        )
        response_times_orig = cursor.fetchone()
        response_times = [t for t in response_times_orig if t is not None]
        n_missing = len(response_times_orig) - len(response_times)
        if response_times:
            return sum(response_times) / len(response_times), n_missing
        return None, n_missing


def fetchall_to_associations(fetchall: List[tuple]) -> List[Association]:
    return [list_to_association(assoc) for assoc in fetchall]


def get_all_associations() -> List[Association]:
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Association")
        l_ass = cursor.fetchall()
        l_ass = fetchall_to_associations(l_ass)
    return l_ass


def update_association(ass: Association):
    association_id = ass.id
    d_modified = ass.get_modified_dict()
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        columns = ", ".join([f"{k} = ?" for k in d_modified])
        values = list(d_modified.values()) + [association_id]
        cursor.execute(
            f"UPDATE Association SET {columns} WHERE id = ?", values
        )
        conn.commit()


def delete_association(assoc_id: int):
    """Delete the corresponding associaction data"""
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Association WHERE id=?", (assoc_id,))
        conn.commit()


def list_to_association(l: List) -> Association:
    return Association(
        id=l[0],
        information=l[1],
        information_image=l[2],
        character_text=l[3],
        pao_image=l[4],
        action_text=l[5],
        object_text=l[6],
        last_response_time_I_to_PAO=l[7],
        last_response_time_P_to_I=l[8],
        last_response_time_A_to_I=l[9],
        last_response_time_O_to_I=l[10],
        creation_date=l[11],
        last_repetition_date=l[12],
        refresh_count=l[13],
        difficulty=l[14],
        retention_index=l[15],
    )


def get_association_by_id(association_id: int) -> Association:
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Association WHERE id=?", (association_id,)
        )
        association = cursor.fetchone()
        return list_to_association(association)


##############################################################################
##############################################################################
# Hourslog database functions


def calculate_retention_index():
    """Calculate the retention index for each association in the database.

    The retention index is
    """
    now = datetime.now()
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Fetch all associations
        cursor.execute("SELECT * FROM Association")
        associations = cursor.fetchall()

        # Calculate mean response time for each association with a refresh count > 0
        l_mean_response_time = []
        for association in associations:
            association_id = association[0]
            refresh_count = association[13]
            if refresh_count > 0:
                mean_single_response_time, n_missing = get_mean_response_time(
                    Association(id=association_id)
                )
                if mean_single_response_time is not None:
                    l_mean_response_time.append(mean_single_response_time)

        # Calculate overall mean response time
        mean_response_time = (
            sum(l_mean_response_time) / len(l_mean_response_time)
            if l_mean_response_time
            else None
        )

        # Update each association with its calculated retention index
        for association in associations:
            association_id = association[0]
            difficulty = association[
                13
            ]  # Assuming difficulty is stored at index 13

            # Adjust difficulty based on mean response time if it exists
            n_missing = 0
            if mean_response_time is not None:
                mean_time, n_missing = get_mean_response_time(
                    Association(id=association_id)
                )
                if mean_time is not None and mean_response_time != 0:
                    difficulty = mean_time / mean_response_time * difficulty

            last_repetition_date = association[
                11
            ]  # Assuming last_repetition_date is stored at index 11
            retention_idx = 0
            if last_repetition_date:
                last_repetition_date = datetime.fromisoformat(
                    last_repetition_date
                )
                retention_idx = retention_index(
                    now - last_repetition_date,
                    association[13],  # refresh_count
                    difficulty,
                )
                retention_idx /= n_missing + 1

            # Update the association with the new retention index
            cursor.execute(
                """
                UPDATE Association
                SET difficulty=?, retention_index=?
                WHERE id=?
            """,
                (difficulty, retention_idx, association_id),
            )

        conn.commit()


def current_state() -> bool:
    """Determines the current state based on the most recent work log entry.
    Returns True if the last log entry is a check-in, False if it is a check-out or no logs are found.
    """
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Select the last work log entry
        cursor.execute(
            "SELECT check_in FROM WorkLog ORDER BY timestamp DESC LIMIT 1"
        )
        log = cursor.fetchone()

        # print("Log:", log)
        if log is None:
            return False  # No log found

        return bool(log[0])  # Returns True if check_in is 1, False otherwise


# Funzioni per i log di lavoro
def set_work_log(check_in: bool, time: datetime) -> int:
    today = time.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM WorkDay WHERE date=?", (today,))
        work_day_id = cursor.fetchone()

        if work_day_id is None:
            cursor.execute("INSERT INTO WorkDay (date) VALUES (?)", (today,))
            work_day_id = cursor.lastrowid
        else:
            work_day_id = work_day_id[0]

        cursor.execute(
            """
            INSERT INTO WorkLog (timestamp, check_in, workday_id) 
            VALUES (?, ?, ?)
        """,
            (time.isoformat(), int(check_in), work_day_id),
        )
        uid = cursor.lastrowid
        conn.commit()

    return uid


def get_worked_hours_today() -> timedelta:
    today = (
        datetime.now()
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .isoformat()
    )
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM WorkDay WHERE date=?", (today,))
        work_day_id = cursor.fetchone()

        if work_day_id is None:
            return timedelta(0)

        work_day_id = work_day_id[0]
        # Fetch all work logs for the day
        cursor.execute(
            "SELECT timestamp, check_in FROM WorkLog WHERE workday_id=?",
            (work_day_id,),
        )
        work_logs = cursor.fetchall()
        # Find the last check-in time
        time_of_work = timedelta(0)
        lunch_break = timedelta(0)
        work_break = timedelta(0)
        last_check_in = None
        len_work_logs = len(work_logs)
        if len_work_logs % 2 != 0:
            len_work_logs -= 1
            last_check_in = datetime.fromisoformat(work_logs[-1][0])
        for i in range(0, len_work_logs, 2):
            start_time = datetime.fromisoformat(work_logs[i][0])
            end_time = datetime.fromisoformat(work_logs[i + 1][0])
            time_of_work += end_time - start_time

            if i > 0:
                prev_end_time = datetime.fromisoformat(work_logs[i - 1][0])
                if 11 <= prev_end_time.hour <= 14:
                    lunch_break += start_time - prev_end_time
                else:
                    work_break += start_time - prev_end_time

    # Convert time worked to hours:minutes:seconds format
    if last_check_in is not None:
        time_of_work += datetime.now() - last_check_in
    time_of_work = str(time_of_work).split(".")[0]
    return time_of_work


def analyze_hours():
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date FROM WorkDay")
        work_days = cursor.fetchall()

        for work_day in work_days:
            work_day_id = work_day[0]
            cursor.execute(
                "SELECT timestamp, check_in FROM WorkLog WHERE workday_id=?",
                (work_day_id,),
            )
            work_logs = cursor.fetchall()
            time_of_work = timedelta(0)
            lunch_break = timedelta(0)
            work_break = timedelta(0)

            if len(work_logs) % 2 != 0:
                work_logs = work_logs[:-1]

            for i in range(0, len(work_logs), 2):
                start_time = datetime.fromisoformat(work_logs[i][0])
                end_time = datetime.fromisoformat(work_logs[i + 1][0])
                time_of_work += end_time - start_time

                if i > 0:
                    prev_end_time = datetime.fromisoformat(work_logs[i - 1][0])
                    if 11 <= prev_end_time.hour <= 14:
                        lunch_break += start_time - prev_end_time
                    else:
                        work_break += start_time - prev_end_time

            cursor.execute(
                """
                UPDATE WorkDay SET time_of_work=?, lunch_break=?, work_break=? WHERE id=?
            """,
                (
                    str(time_of_work),
                    str(lunch_break),
                    str(work_break),
                    work_day_id,
                ),
            )
        conn.commit()


def get_hourslog_data_summary():
    """Fetch workday data and structure it as a list of dictionaries
    for display.

    Returns:
        list: A list of dictionaries containing workday data with the following
            keys: workday_id, date, work_time, lunch_break, work_break.
            all are strings.
    """
    from siapp.db.models import DATABASE

    analyze_hours()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, time_of_work, lunch_break, work_break, id FROM WorkDay"
        )
        work_days = cursor.fetchall()
        return [
            {
                "workday_id": wd[4],
                "date": wd[0].split("T")[0] if wd[0] else "",
                "work_time": wd[1].split(".")[0] if wd[1] else "",
                "lunch_break": wd[2].split(".")[0] if wd[2] else "",
                "work_break": wd[3].split(".")[0] if wd[3] else "",
            }
            for wd in work_days
        ]


def get_last_workday_id() -> int:
    """Get the ID of the last workday in the database."""
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM WorkDay ORDER BY id DESC LIMIT 1")
        workday_id = cursor.fetchone()
        return workday_id[0] if workday_id else 0


def get_worklog_data_summary(workday_id: int):
    """Fetch work log data for a specific workday and structure it as a list of dictionaries for display.

    Args:
        workday_id (int): The ID of the workday to fetch work log data for.

    Returns:
        list: A list of dictionaries containing work log data with the following keys: worklog_id, timestamp, check_in.
        All are strings.
    """
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, check_in FROM WorkLog WHERE workday_id=?",
            (workday_id,),
        )
        logs = cursor.fetchall()
        return [
            {
                "uid": log[0],
                "timestamp": log[1].split("T")[1].split(".")[0],
                "check_in": log[2],
            }
            for log in logs
        ]


def delete_workday_entry(workday_id: int):
    """Delete a workday entry and its associated work logs from the database."""
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # GEt the work logs associated with the workday
        cursor.execute(
            "SELECT id FROM WorkLog WHERE workday_id=?", (workday_id,)
        )
        work_logs = cursor.fetchall()
        # Delete the work logs
        for log in work_logs:
            cursor.execute("DELETE FROM WorkLog WHERE id=?", (log[0],))
        cursor.execute("DELETE FROM WorkDay WHERE id=?", (workday_id,))
        conn.commit()


def delete_worlkog_entry(worklog_id: int):
    """Delete a worklog entry from the database."""
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM WorkLog WHERE id=?", (worklog_id,))
        conn.commit()


def get_hourslog_export_data() -> list:
    """Fetch workday and work log data, structure it as a list of dictionaries for CSV export."""
    from siapp.db.models import DATABASE

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Query for all workdays
        cursor.execute(
            "SELECT id, date, time_of_work, lunch_break, work_break FROM WorkDay"
        )
        work_days = cursor.fetchall()

        data = []
        for work_day in work_days:
            workday_id, date, time_of_work, lunch_break, work_break = work_day
            d_workday = {
                "Day": date.split("T")[0],
                "Work Time": time_of_work.split(".")[0],
                "Lunch Break": lunch_break.split(".")[0],
                "Pause": work_break.split(".")[0],
            }

            # Fetch associated work logs for each work day
            cursor.execute(
                "SELECT timestamp, check_in FROM WorkLog WHERE workday_id=? ORDER BY timestamp",
                (workday_id,),
            )
            work_logs = cursor.fetchall()

            # Pair the logs as "in" and "out" timestamps
            for i, log in enumerate(work_logs):
                timestamp, check_in = log
                timestamp = datetime.fromisoformat(timestamp).strftime("%H:%M")
                if i % 2 == 0:
                    d_workday[f"In {i//2 + 1}"] = timestamp
                else:
                    d_workday[f"Out {i//2 + 1}"] = timestamp

            data.append(d_workday)

    return data


def save_exported_data(output_folder: Path):
    """Export the work data to a CSV file in the specified output folder."""
    data = get_hourslog_export_data()
    filename = Path("HoursLog.csv")
    output_file = Path(output_folder) / filename.name

    # Write data to CSV
    with open(output_file, mode="w", newline="") as file:
        # Dynamically get field names from the data to handle varying keys (e.g., different "in/out" columns)
        fieldnames = {key for row in data for key in row.keys()}
        fields_start = [
            f for f in fieldnames if "In " not in f and "Out " not in f
        ]
        fields_end = [f for f in fieldnames if "In " in f or "Out " in f]
        n_fields_end = len(fields_end)
        fields_end_last = []
        for i in range(n_fields_end):
            if i % 2 == 0:
                fields_end_last.append(f"In {i//2 + 1}")
            else:
                fields_end_last.append(f"Out {i//2 + 1}")
        fieldnames = fields_start + fields_end_last
        print("Fieldnames:", fieldnames)
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
