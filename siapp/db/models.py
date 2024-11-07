from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional


class Association(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    information: str
    character_text: Optional[str] = None
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


# Setup database
engine = create_engine("sqlite:///memory_app.db")
SQLModel.metadata.create_all(engine)
