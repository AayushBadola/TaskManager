
from typing import Dict, Generator
from .models import Task

fake_db: Dict[int, Task] = {}
_next_id: int = 1

def get_db() -> Generator[Dict[int, Task], None, None]:
    try:
        yield fake_db
    finally:
        pass

def get_next_id() -> int:
    global _next_id
    current_id = _next_id
    _next_id += 1
    return current_id

def reset_db_for_testing() -> None:
    global fake_db, _next_id
    fake_db = {}
    _next_id = 1
