"""Tests for SQLite database initialization, CSV import, and data integrity."""

import csv
from pathlib import Path
import sqlite3
import pytest

from database.connection import (
    DEFAULT_DB_PATH,
    execute_query,
    fetch_all,
    fetch_one,
    get_connection,
)
from database.csv_importer import (
    find_default_csv,
    import_csv_to_sqlite,
    init_student_table,
)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Fixture providing a temporary SQLite database file path."""
    db_file = tmp_path / "test_student.db"
    return db_file


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Fixture providing a sample student CSV file with valid and edge case rows."""
    csv_file = tmp_path / "sample_students.csv"
    rows = [
        ["student_id", "name", "branch", "semester", "attendance_percent", "cgpa", "backlogs", "attendance_status"],
        ["STU001", "Aarav Sharma", "ECE", "6", "82.5", "7.8", "0", "Eligible"],
        ["STU002", "Riya Mehta", "CSE", "6", "76.0", "8.4", "0", "Eligible"],
        ["STU003", "Arjun Verma", "CSE", "6", "59.0", "6.8", "2", "Not Eligible"],
    ]
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return csv_file


def test_database_creation(temp_db: Path) -> None:
    """Test that the database file and table are created successfully."""
    init_student_table(temp_db)
    assert temp_db.is_file()

    conn = get_connection(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students';")
    table = cursor.fetchone()
    conn.close()
    assert table is not None
    assert table["name"] == "students"


def test_csv_import_row_count(temp_db: Path, sample_csv: Path) -> None:
    """Test that all CSV rows are correctly imported into the database."""
    result = import_csv_to_sqlite(sample_csv, temp_db)
    assert result["rows_imported"] == 3

    rows = fetch_all("SELECT * FROM students ORDER BY student_id ASC;", db_path=temp_db)
    assert len(rows) == 3
    assert rows[0]["student_id"] == "STU001"
    assert rows[0]["name"] == "Aarav Sharma"
    assert rows[0]["branch"] == "ECE"
    assert rows[0]["semester"] == 6
    assert rows[0]["attendance_percent"] == 82.5
    assert rows[0]["cgpa"] == 7.8
    assert rows[0]["backlogs"] == 0
    assert rows[0]["attendance_status"] == "Eligible"


def test_csv_import_default_dataset(temp_db: Path) -> None:
    """Test importing the default tabular dataset (CSV or XLSX)."""
    csv_path = find_default_csv()
    assert Path(csv_path).is_file(), f"Default file not found at {csv_path}"

    result = import_csv_to_sqlite(csv_path, temp_db)
    assert result["rows_imported"] == 30


def test_csv_import_idempotency(temp_db: Path, sample_csv: Path) -> None:
    """Test that re-running the CSV import does not create duplicate rows."""
    result1 = import_csv_to_sqlite(sample_csv, temp_db)
    assert result1["rows_imported"] == 3

    # Re-run import
    result2 = import_csv_to_sqlite(sample_csv, temp_db)
    assert result2["rows_imported"] == 3

    rows = fetch_all("SELECT * FROM students;", db_path=temp_db)
    assert len(rows) == 3


def test_csv_import_handles_empty_and_null_values(tmp_path: Path, temp_db: Path) -> None:
    """Test that empty strings and missing numerical fields in CSV are safely handled."""
    csv_file = tmp_path / "edge_case_students.csv"
    rows = [
        ["student_id", "name", "branch", "semester", "attendance_percent", "cgpa", "backlogs", "attendance_status"],
        ["STU999", "Edge Case Student", "IT", "", "", "", "", ""],
    ]
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    result = import_csv_to_sqlite(csv_file, temp_db)
    assert result["rows_imported"] == 1

    row = fetch_one("SELECT * FROM students WHERE student_id = 'STU999';", db_path=temp_db)
    assert row is not None
    assert row["student_id"] == "STU999"
    assert row["name"] == "Edge Case Student"
    assert row["semester"] == 1  # default fallback
    assert row["attendance_percent"] == 0.0
    assert row["cgpa"] == 0.0
    assert row["backlogs"] == 0
    assert row["attendance_status"] == "Not Eligible"


def test_parameterized_query_and_sql_injection_defense(temp_db: Path, sample_csv: Path) -> None:
    """Test that parameterized queries prevent SQL injection payloads."""
    import_csv_to_sqlite(sample_csv, temp_db)

    # Attempt standard SQL injection payload as student_id
    malicious_input = "' OR '1'='1"
    row = fetch_one(
        "SELECT * FROM students WHERE student_id = ?;",
        (malicious_input,),
        db_path=temp_db,
    )
    assert row is None


def test_database_persistence_across_connections(temp_db: Path, sample_csv: Path) -> None:
    """Test that records persist in the SQLite file across independent connection closures."""
    import_csv_to_sqlite(sample_csv, temp_db)

    # Open and close connection 1
    conn1 = get_connection(temp_db)
    assert conn1.execute("SELECT COUNT(*) FROM students;").fetchone()[0] == 3
    conn1.close()

    # Open connection 2 and verify data is retained
    conn2 = get_connection(temp_db)
    assert conn2.execute("SELECT COUNT(*) FROM students;").fetchone()[0] == 3
    conn2.close()
