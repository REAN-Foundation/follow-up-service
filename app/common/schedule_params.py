from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel, Field

class ScheduleParams(BaseModel):
    date: List[str]
    time: str
