import sqlite3
from typing import Any


class BaseStorage:
    def __init__(self, db_name: str) -> None:
        self.connection = sqlite3.connect(db_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.connection.close()
        del self.connection
        del self
