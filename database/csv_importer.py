"""Import structured student and tabular records (CSV, XLSX, XLS) into SQLite."""

import argparse
import csv
from pathlib import Path
import sys
from typing import Any

from database.connection import (
    DEFAULT_DB_PATH,
    get_connection,
    get_db_cursor,
)

# Potential tabular locations in order of precedence
CANDIDATE_DATA_PATHS = [
    Path("data/documents/MindMesh_30_Synthetic_Students.csv"),
    Path("data/documents/login_data.xlsx"),
    Path("login_data.xlsx"),
    Path("data/student_data.csv"),
    Path("MindMesh_30_Synthetic_Students.csv"),
]

DEFAULT_FILE_PATH = CANDIDATE_DATA_PATHS[0]
DEFAULT_CSV_PATH = DEFAULT_FILE_PATH


def find_default_file() -> Path:
    """Locate the default data file among expected project paths."""
    for path in CANDIDATE_DATA_PATHS:
        if path.is_file():
            return path
    return DEFAULT_FILE_PATH


def find_default_csv() -> Path:
    """Backward-compatible helper to locate default student file."""
    return find_default_file()


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


def _read_table_rows(file_path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    """Extract column headers and dictionary rows from CSV, XLSX, or XLS files."""
    suffix = file_path.suffix.lower()

    if suffix in {".xlsx", ".xlsm"}:
        import openpyxl

        wb = openpyxl.load_workbook(str(file_path), data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
        wb.close()
        if not rows:
            return [], []

        raw_headers = [str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
        headers = [h.lower() for h in raw_headers]
        data = []
        for r in rows[1:]:
            if not any(v is not None and str(v).strip() != "" for v in r):
                continue
            row_dict = {}
            for i, h in enumerate(headers):
                val = r[i] if i < len(r) else None
                row_dict[h] = val
            data.append(row_dict)
        return headers, data

    if suffix == ".xls":
        import xlrd

        wb = xlrd.open_workbook(str(file_path))
        sheet = wb.sheet_by_index(0)
        if sheet.nrows == 0:
            return [], []
        headers = [str(h).strip().lower() for h in sheet.row_values(0)]
        data = []
        for r_idx in range(1, sheet.nrows):
            r = sheet.row_values(r_idx)
            if not any(v is not None and str(v).strip() != "" for v in r):
                continue
            row_dict = {headers[i]: r[i] for i in range(min(len(headers), len(r)))}
            data.append(row_dict)
        return headers, data

    # Default CSV loader
    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            cleaned_row = {k.strip().lower(): v for k, v in row.items() if k is not None}
            data.append(cleaned_row)
        headers = [h.strip().lower() for h in reader.fieldnames or []]
        return headers, data


def init_user_table(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    """Create the users/login table if it does not already exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        student_id TEXT PRIMARY KEY,
        student_name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    );
    """
    with get_db_cursor(db_path) as cursor:
        cursor.execute(create_table_sql)


def import_login_data_to_sqlite(
    file_path: str | Path,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Import login credentials into the SQLite users table."""
    target_file = Path(file_path)
    if not target_file.is_file():
        raise FileNotFoundError(f"File not found at '{target_file}'")

    headers, rows = _read_table_rows(target_file)
    init_user_table(db_path)

    insert_sql = """
    INSERT INTO users (student_id, student_name, email, password)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(student_id) DO UPDATE SET
        student_name = excluded.student_name,
        email = excluded.email,
        password = excluded.password;
    """

    records = []
    for idx, row in enumerate(rows, start=1):
        student_id = str(row.get("student_id") or row.get("id") or f"STU{idx:03d}").strip()
        student_name = str(row.get("student_name") or row.get("name") or student_id).strip()
        email = str(row.get("nsut_email") or row.get("email") or "").strip()
        password = str(row.get("test_password") or row.get("password") or "").strip()

        if student_id:
            records.append((student_id, student_name, email, password))

    with get_db_cursor(db_path) as cursor:
        cursor.executemany(insert_sql, records)

    return {
        "rows_imported": len(records),
        "file_path": str(target_file),
        "db_path": str(Path(db_path).resolve()),
        "table_name": "users",
    }


def import_csv_to_sqlite(
    file_path: str | Path = DEFAULT_FILE_PATH,
    db_path: str | Path = DEFAULT_DB_PATH,
    table_name: str = "students",
) -> dict[str, Any]:
    """Import student records or login data from CSV or XLSX into SQLite."""
    target_file = Path(file_path)
    if not target_file.is_file():
        raise FileNotFoundError(
            f"Data file not found at '{target_file}'. Please verify the file path."
        )

    headers, rows = _read_table_rows(target_file)

    # Check if this is a login/credentials file
    is_login_file = any("email" in h or "password" in h for h in headers)
    if is_login_file and table_name == "students":
        return import_login_data_to_sqlite(target_file, db_path)

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

    records_to_insert = []
    for idx, row in enumerate(rows, start=1):
        student_id = str(
            row.get("student_id") or row.get("id") or row.get("roll_no") or row.get("username") or f"STU{idx:04d}"
        ).strip()
        if not student_id:
            continue

        name = str(row.get("name") or row.get("student_name") or row.get("user") or student_id).strip()
        branch = str(row.get("branch") or row.get("department") or "General").strip()
        semester = _parse_safe_int(row.get("semester"), default=1)
        attendance_percent = _parse_safe_float(row.get("attendance_percent") or row.get("attendance"), default=0.0)
        cgpa = _parse_safe_float(row.get("cgpa") or row.get("gpa"), default=0.0)
        backlogs = _parse_safe_int(row.get("backlogs") or row.get("active_backlogs"), default=0)
        attendance_status = str(row.get("attendance_status") or "").strip() or (
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

    with get_db_cursor(db_path) as cursor:
        cursor.executemany(insert_sql, records_to_insert)

    return {
        "rows_imported": len(records_to_insert),
        "file_path": str(target_file),
        "db_path": str(Path(db_path).resolve()),
        "table_name": table_name,
    }


def main() -> None:
    """CLI entry point for importing student CSV/Excel data into SQLite."""
    parser = argparse.ArgumentParser(description="Import CSV/XLSX records into SQLite database.")
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Path to CSV or XLSX file to import (e.g., login_data.xlsx or data/documents/login_data.xlsx)",
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )
    args = parser.parse_args()

    file_path = Path(args.file) if args.file else find_default_file()
    db_path = Path(args.db)

    print(f"Importing records from: {file_path}")
    print(f"Target SQLite database: {db_path}")

    try:
        result = import_csv_to_sqlite(file_path, db_path)
        print("\n--- Import Successful ---")
        print(f"Table Name:    {result['table_name']}")
        print(f"Rows Imported: {result['rows_imported']}")
        print(f"Database Path: {result['db_path']}")
    except Exception as error:
        print(f"\n[ERROR] Import failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


