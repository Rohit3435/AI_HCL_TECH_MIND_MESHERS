"""Import structured student CSV records into a persistent SQLite database."""

import csv
from pathlib import Path
import sys
from typing import Any

from database.connection import (
    DEFAULT_DB_PATH,
    get_connection,
    get_db_cursor,
)

# Potential CSV locations in order of precedence
CANDIDATE_CSV_PATHS = [
    Path("data/documents/MindMesh_30_Synthetic_Students.csv"),
    Path("data/student_data.csv"),
    Path("MindMesh_30_Synthetic_Students.csv"),
]

DEFAULT_CSV_PATH = CANDIDATE_CSV_PATHS[0]


def find_default_csv() -> Path:
    """Locate the student CSV file among expected project paths."""
    for path in CANDIDATE_CSV_PATHS:
        if path.is_file():
            return path
    return DEFAULT_CSV_PATH


def init_student_table(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    """Create the students table if it does not already exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        branch TEXT NOT NULL,
        semester INTEGER NOT NULL,
        attendance_percent REAL NOT NULL,
        cgpa REAL NOT NULL,
        backlogs INTEGER NOT NULL,
        attendance_status TEXT NOT NULL
    );
    """
    with get_db_cursor(db_path) as cursor:
        cursor.execute(create_table_sql)


def _parse_safe_int(value: Any, default: int = 0) -> int:
    """Convert a value safely to integer, returning default if empty or invalid."""
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return int(float(text))
    except (ValueError, TypeError):
        return default


def _parse_safe_float(value: Any, default: float = 0.0) -> float:
    """Convert a value safely to float, returning default if empty or invalid."""
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return float(text)
    except (ValueError, TypeError):
        return default


def import_csv_to_sqlite(
    csv_path: str | Path = DEFAULT_CSV_PATH,
    db_path: str | Path = DEFAULT_DB_PATH,
    table_name: str = "students",
) -> dict[str, Any]:
    """Import student records from a CSV file into SQLite using parameterized queries.

    This operation is idempotent: re-importing the same CSV updates existing records
    and inserts new records without creating duplicates.
    """
    csv_file = Path(csv_path)
    if not csv_file.is_file():
        raise FileNotFoundError(
            f"CSV file not found at '{csv_file}'. Please verify the file path."
        )

    # Ensure table exists
    init_student_table(db_path)

    insert_sql = f"""
    INSERT INTO {table_name} (
        student_id, name, branch, semester, attendance_percent, cgpa, backlogs, attendance_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(student_id) DO UPDATE SET
        name = excluded.name,
        branch = excluded.branch,
        semester = excluded.semester,
        attendance_percent = excluded.attendance_percent,
        cgpa = excluded.cgpa,
        backlogs = excluded.backlogs,
        attendance_status = excluded.attendance_status;
    """

    rows_processed = 0
    records_to_insert = []

    with open(csv_file, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize keys to lowercase stripped
            cleaned_row = {k.strip().lower(): v for k, v in row.items() if k is not None}
            
            student_id = cleaned_row.get("student_id", "").strip()
            if not student_id:
                continue

            name = cleaned_row.get("name", "").strip()
            branch = cleaned_row.get("branch", "").strip()
            semester = _parse_safe_int(cleaned_row.get("semester"), default=1)
            attendance_percent = _parse_safe_float(cleaned_row.get("attendance_percent"), default=0.0)
            cgpa = _parse_safe_float(cleaned_row.get("cgpa"), default=0.0)
            backlogs = _parse_safe_int(cleaned_row.get("backlogs"), default=0)
            attendance_status = cleaned_row.get("attendance_status", "").strip() or (
                "Eligible" if attendance_percent >= 75.0 else "Not Eligible"
            )

            records_to_insert.append((
                student_id,
                name,
                branch,
                semester,
                attendance_percent,
                cgpa,
                backlogs,
                attendance_status,
            ))
            rows_processed += 1

    with get_db_cursor(db_path) as cursor:
        cursor.executemany(insert_sql, records_to_insert)

    return {
        "rows_imported": rows_processed,
        "csv_path": str(csv_file),
        "db_path": str(Path(db_path).resolve()),
        "table_name": table_name,
    }


def main() -> None:
    """CLI entry point for importing student CSV data into SQLite."""
    csv_path = find_default_csv()
    db_path = DEFAULT_DB_PATH

    print(f"Importing student data from: {csv_path}")
    print(f"Target SQLite database:      {db_path}")

    try:
        result = import_csv_to_sqlite(csv_path, db_path)
        print("\n--- Import Successful ---")
        print(f"Table Name:    {result['table_name']}")
        print(f"Rows Imported: {result['rows_imported']}")
        print(f"Database Path: {result['db_path']}")
    except Exception as error:
        print(f"\n[ERROR] CSV import failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
