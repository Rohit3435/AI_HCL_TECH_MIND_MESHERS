"""SQLite database connection and query helpers for student data."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Any, Generator

DEFAULT_DB_PATH = Path("database/student.db")


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open and return a persistent SQLite connection with row access by column name."""
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db_cursor(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for SQLite operations ensuring commits, rollbacks, and close."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def execute_query(
    query: str,
    params: tuple[Any, ...] | list[Any] = (),
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    """Execute a parameterized query and return the number of affected rows."""
    with get_db_cursor(db_path) as cursor:
        cursor.execute(query, params)
        return cursor.rowcount


def fetch_one(
    query: str,
    params: tuple[Any, ...] | list[Any] = (),
    db_path: str | Path = DEFAULT_DB_PATH,
) -> dict[str, Any] | None:
    """Execute a parameterized SELECT query and return a single row as a dictionary."""
    with get_db_cursor(db_path) as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)


def fetch_all(
    query: str,
    params: tuple[Any, ...] | list[Any] = (),
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Execute a parameterized SELECT query and return all rows as a list of dictionaries."""
    with get_db_cursor(db_path) as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
