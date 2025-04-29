from pydantic import BaseModel, Field
from typing import Optional

class Task(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: bool = False

