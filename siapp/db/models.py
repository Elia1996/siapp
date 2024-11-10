import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
from kivy.utils import platform
from kivy.app import App


# Database file
if platform == "android":
    DATABASE = App.get_running_app().user_data_dir + "/memory_app.db"
else:
    DATABASE = "memory_app.db"


class Association:
    def __init__(
        self,
        id: Optional[int] = None,  # 0
        information: str = "",  # 1
        information_image: Optional[bytes] = None,  # 2
        character_text: Optional[str] = None,  # 3
        pao_image: Optional[bytes] = None,  # 4
        action_text: Optional[str] = None,  # 5
        object_text: Optional[str] = None,  # 6
        last_response_time_I_to_PAO: Optional[float] = None,  # 7
        last_response_time_P_to_I: Optional[float] = None,  # 8
        last_response_time_A_to_I: Optional[float] = None,  # 9
        last_response_time_O_to_I: Optional[float] = None,  # 10
        creation_date: Optional[str] = None,  # 11
        last_repetition_date: Optional[str] = None,  # 12
        refresh_count: Optional[int] = None,  # 13
        difficulty: Optional[float] = None,  # 14
        retention_index: Optional[float] = None,  # 15
    ):
        self._data = {}
        self._data["id"] = id
        self._data["information"] = information
        self._data["information_image"] = information_image
        self._data["character_text"] = character_text
        self._data["pao_image"] = pao_image
        self._data["action_text"] = action_text
        self._data["object_text"] = object_text
        self._data["last_response_time_I_to_PAO"] = last_response_time_I_to_PAO
        self._data["last_response_time_P_to_I"] = last_response_time_P_to_I
        self._data["last_response_time_A_to_I"] = last_response_time_A_to_I
        self._data["last_response_time_O_to_I"] = last_response_time_O_to_I
        self._data["creation_date"] = creation_date
        self._data["last_repetition_date"] = last_repetition_date
        self._data["refresh_count"] = refresh_count
        self._data["difficulty"] = difficulty
        self._data["retention_index"] = retention_index
        self._changed = []

    @property
    def id(self) -> Optional[int]:
        return self._data["id"]

    @property
    def information(self) -> str:
        return self._data["information"]

    @information.setter
    def information(self, value: str):
        self._data["information"] = value
        self._changed.append("information")

    @property
    def information_image(self) -> Optional[bytes]:
        return self._data["information_image"]

    @information_image.setter
    def information_image(self, value: Optional[bytes]):
        self._data["information_image"] = value
        self._changed.append("information_image")

    @property
    def character_text(self) -> Optional[str]:
        return self._data["character_text"]

    @character_text.setter
    def character_text(self, value: Optional[str]):
        self._data["character_text"] = value
        self._changed.append("character_text")

    @property
    def pao_image(self) -> Optional[bytes]:
        return self._data["pao_image"]

    @pao_image.setter
    def pao_image(self, value: Optional[bytes]):
        self._data["pao_image"] = value
        self._changed.append("pao_image")

    @property
    def action_text(self) -> Optional[str]:
        return self._data["action_text"]

    @action_text.setter
    def action_text(self, value: Optional[str]):
        self._data["action_text"] = value
        self._changed.append("action_text")

    @property
    def object_text(self) -> Optional[str]:
        return self._data["object_text"]

    @object_text.setter
    def object_text(self, value: Optional[str]):
        self._data["object_text"] = value
        self._changed.append("object_text")

    @property
    def last_response_time_I_to_PAO(self) -> Optional[float]:
        return self._data["last_response_time_I_to_PAO"]

    @last_response_time_I_to_PAO.setter
    def last_response_time_I_to_PAO(self, value: Optional[float]):
        self._data["last_response_time_I_to_PAO"] = value
        self._changed.append("last_response_time_I_to_PAO")

    @property
    def last_response_time_P_to_I(self) -> Optional[float]:
        return self._data["last_response_time_P_to_I"]

    @last_response_time_P_to_I.setter
    def last_response_time_P_to_I(self, value: Optional[float]):
        self._data["last_response_time_P_to_I"] = value
        self._changed.append("last_response_time_P_to_I")

    @property
    def last_response_time_A_to_I(self) -> Optional[float]:
        return self._data["last_response_time_A_to_I"]

    @last_response_time_A_to_I.setter
    def last_response_time_A_to_I(self, value: Optional[float]):
        self._data["last_response_time_A_to_I"] = value
        self._changed.append("last_response_time_A_to_I")

    @property
    def creation_date(self) -> Optional[str]:
        return self._data["creation_date"]

    @creation_date.setter
    def creation_date(self, value: Optional[str]):
        self._data["creation_date"] = value
        self._changed.append("creation_date")

    @property
    def last_repetition_date(self) -> Optional[str]:
        return self._data["last_repetition_date"]

    @last_repetition_date.setter
    def last_repetition_date(self, value: Optional[str]):
        self._data["last_repetition_date"] = value
        self._changed.append("last_repetition_date")

    @property
    def refresh_count(self) -> Optional[int]:
        return self._data["refresh_count"]

    @refresh_count.setter
    def refresh_count(self, value: Optional[int]):
        self._data["refresh_count"] = value
        self._changed.append("refresh_count")

    @property
    def difficulty(self) -> Optional[float]:
        return self._data["difficulty"]

    @difficulty.setter
    def difficulty(self, value: Optional[float]):
        self._data["difficulty"] = value
        self._changed.append("difficulty")

    @property
    def retention_index(self) -> Optional[float]:
        return self._data["retention_index"]

    @retention_index.setter
    def retention_index(self, value: Optional[float]):
        self._data["retention_index"] = value
        self._changed.append("retention_index")

    def get_modified_dict(self):
        return {k: self._data[k] for k in self._changed}


# Setup database and create tables
def create_tables():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Association (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            information TEXT,
            information_image BLOB,
            character_text TEXT,
            pao_image BLOB,
            action_text TEXT,
            object_text TEXT,
            last_response_time_I_to_PAO REAL,
            last_response_time_P_to_I REAL,
            last_response_time_A_to_I REAL,
            last_response_time_O_to_I REAL,
            creation_date TEXT,
            last_repetition_date TEXT,
            refresh_count INTEGER,
            difficulty REAL,
            retention_index REAL
        )"""
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS WorkDay (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time_of_work TEXT,
            lunch_break TEXT,
            work_break TEXT
        )"""
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS WorkLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            check_in INTEGER,
            workday_id INTEGER,
            FOREIGN KEY (workday_id) REFERENCES WorkDay(id)
        )"""
        )
    conn.close()


# Check if the database is created, if yes don't create it again
def check_database():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Association")
            cursor.execute("SELECT * FROM WorkDay")
            cursor.execute("SELECT * FROM WorkLog")
        conn.close()
    except sqlite3.OperationalError:
        create_tables()


check_database()
