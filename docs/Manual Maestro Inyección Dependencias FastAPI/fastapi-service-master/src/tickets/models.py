from typing import Optional
from sqlmodel import SQLModel, Field

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    is_completed: bool = Field(default=False)
    priority: Optional[int] = Field(default=1, ge=1, le=5)  # Priority from 1 (low) to 5 (high)