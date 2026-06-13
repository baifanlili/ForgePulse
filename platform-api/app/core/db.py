from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from app.core.config import get_settings


@contextmanager
def db_cursor() -> Iterator[psycopg.Cursor[dict[str, Any]]]:
    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            yield cur
