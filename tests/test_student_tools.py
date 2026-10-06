"""Tests for deterministic student SQL tools and structured response contracts."""

from pathlib import Path
import pytest

from database.csv_importer import import_csv_to_sqlite, find_default_csv
from tools.student_tools import (
    get_student_details,
    get_student_attendance,
    get_student_cgpa,
    get_student_backlogs,
    get_student_eligibility_status,
    list_students,
)


@pytest.fixture
def populated_db(tmp_path: Path) -> Path:
    """Fixture providing a database populated with default synthetic student records."""
    db_file = tmp_path / "test_students.db"
    csv_file = find_default_csv()
    import_csv_to_sqlite(csv_file, db_file)
    return db_file


def test_get_student_details_existing(populated_db: Path) -> None:
    """Test retrieving full student profile for a valid student ID."""
    result = get_student_details("STU001", db_path=populated_db)
    assert result["status"] == "FOUND"
    assert result["student_id"] == "STU001"
    assert result["source"] == "sqlite:students"
    assert result["data"]["name"] == "Aarav Sharma"
    assert result["data"]["branch"] == "ECE"
    assert result["data"]["attendance_percent"] == 82.5
    assert result["data"]["cgpa"] == 7.8
    assert result["data"]["backlogs"] == 0


def test_get_student_details_non_existing(populated_db: Path) -> None:
    """Test response contract when querying a non-existent student ID."""
    result = get_student_details("STU999", db_path=populated_db)
    assert result["status"] == "NOT_FOUND"
    assert result["student_id"] == "STU999"
    assert result["data"] is None
    assert result["source"] == "sqlite:students"


def test_get_student_attendance(populated_db: Path) -> None:
    """Test retrieving attendance and status for a student."""
    result = get_student_attendance("STU005", db_path=populated_db)
    assert result["status"] == "FOUND"
    assert result["data"]["name"] == "Arjun Verma"
    assert result["data"]["attendance_percent"] == 59.0
    assert result["data"]["attendance_status"] == "Not Eligible"


def test_get_student_cgpa(populated_db: Path) -> None:
    """Test retrieving CGPA and branch info."""
    result = get_student_cgpa("STU004", db_path=populated_db)
    assert result["status"] == "FOUND"
    assert result["data"]["name"] == "Ananya Gupta"
    assert result["data"]["cgpa"] == 9.0
    assert result["data"]["branch"] == "ECE"


def test_get_student_backlogs(populated_db: Path) -> None:
    """Test retrieving student backlog count."""
    result = get_student_backlogs("STU023", db_path=populated_db)
    assert result["status"] == "FOUND"
    assert result["data"]["name"] == "Harsh Vardhan"
    assert result["data"]["backlogs"] == 3


def test_get_student_eligibility_status(populated_db: Path) -> None:
    """Test retrieving student exam/placement eligibility flag."""
    result = get_student_eligibility_status("STU002", db_path=populated_db)
    assert result["status"] == "FOUND"
    assert result["data"]["attendance_status"] == "Eligible"


def test_list_students(populated_db: Path) -> None:
    """Test listing all students from the database."""
    students = list_students(db_path=populated_db)
    assert len(students) == 30
    assert students[0]["student_id"] == "STU001"
    assert students[-1]["student_id"] == "STU030"
