from sqlmodel import SQLModel, Field, create_engine, Relationship
from datetime import datetime, timedelta
from typing import List, Optional


class Association(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    information: str
    information_image: Optional[bytes] = None
    character_text: Optional[str] = None
    pao_image: Optional[bytes] = None
    action_text: Optional[str] = None
    object_text: Optional[str] = None
    last_response_time_I_to_PAO: Optional[float] = None
    last_response_time_P_to_I: Optional[float] = None
    last_response_time_A_to_I: Optional[float] = None
    last_response_time_O_to_I: Optional[float] = None
    creation_date: datetime
    last_repetition_date: Optional[datetime] = None
    refresh_count: int = 0
    difficulty: float = 0
    retention_index: float = 0.0


class WorkDay(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    date: datetime
    worklog: List["WorkLog"] = Relationship(back_populates="workday")
    time_of_work: Optional[timedelta] = None
    lunch_break: Optional[timedelta] = None
    work_break: Optional[timedelta] = None


class WorkLog(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    timestamp: datetime
    check_in: bool
    workday_id: Optional[int] = Field(foreign_key="workday.id")
    workday: Optional[WorkDay] = Relationship(back_populates="worklog")


# Setup database
engine = create_engine("sqlite:///memory_app.db")
SQLModel.metadata.create_all(engine)
