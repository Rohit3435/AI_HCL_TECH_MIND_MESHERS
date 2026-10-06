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
    """Fixture providing a database populated with test synthetic student records."""
    import csv
    db_file = tmp_path / "test_students.db"
    csv_file = tmp_path / "students_dataset.csv"
    
    # 30 synthetic student test records
    rows = [
        ["student_id", "name", "branch", "semester", "attendance_percent", "cgpa", "backlogs", "attendance_status"],
        ["STU001", "Aarav Sharma", "ECE", 6, 82.5, 7.8, 0, "Eligible"],
        ["STU002", "Riya Mehta", "CSE", 6, 76.0, 8.4, 0, "Eligible"],
        ["STU003", "Kabir Singh", "IT", 6, 88.0, 6.9, 1, "Eligible"],
        ["STU004", "Ananya Gupta", "ECE", 6, 91.5, 9.0, 0, "Eligible"],
        ["STU005", "Arjun Verma", "CSE", 6, 59.0, 6.8, 2, "Not Eligible"],
        ["STU006", "Ishita Rao", "IT", 6, 78.5, 7.5, 0, "Eligible"],
        ["STU007", "Vivaan Kapoor", "ECE", 6, 68.0, 6.2, 1, "Not Eligible"],
        ["STU008", "Meera Nair", "CSE", 6, 94.0, 9.3, 0, "Eligible"],
        ["STU009", "Aditya Malhotra", "IT", 6, 81.0, 7.9, 0, "Eligible"],
        ["STU010", "Sneha Patel", "ECE", 6, 73.0, 6.5, 0, "Not Eligible"],
        ["STU011", "Rohan Das", "CSE", 6, 85.0, 8.1, 0, "Eligible"],
        ["STU012", "Pooja Hegde", "IT", 6, 89.5, 8.7, 0, "Eligible"],
        ["STU013", "Karan Joshi", "ECE", 6, 62.0, 5.9, 3, "Not Eligible"],
        ["STU014", "Diya Sen", "CSE", 6, 90.0, 8.8, 0, "Eligible"],
        ["STU015", "Manish Pandey", "IT", 6, 77.0, 7.2, 0, "Eligible"],
        ["STU016", "Tanvi Bhatia", "ECE", 6, 84.0, 8.0, 0, "Eligible"],
        ["STU017", "Siddharth Roy", "CSE", 6, 79.5, 7.6, 1, "Eligible"],
        ["STU018", "Neha Kulkarni", "IT", 6, 93.0, 9.1, 0, "Eligible"],
        ["STU019", "Varun Dhawan", "ECE", 6, 71.0, 6.4, 0, "Not Eligible"],
        ["STU020", "Shruti Iyer", "CSE", 6, 87.5, 8.5, 0, "Eligible"],
        ["STU021", "Nikhil Chopra", "IT", 6, 83.0, 7.7, 0, "Eligible"],
        ["STU022", "Kavya Menon", "ECE", 6, 92.0, 8.9, 0, "Eligible"],
        ["STU023", "Harsh Vardhan", "CSE", 6, 64.0, 6.1, 3, "Not Eligible"],
        ["STU024", "Simran Kaur", "IT", 6, 86.0, 8.3, 0, "Eligible"],
        ["STU025", "Amitabh Bachan", "ECE", 6, 80.0, 7.4, 0, "Eligible"],
        ["STU026", "Deepika Pad", "CSE", 6, 95.0, 9.5, 0, "Eligible"],
        ["STU027", "Ranbir K", "IT", 6, 74.0, 6.7, 1, "Not Eligible"],
        ["STU028", "Alia B", "ECE", 6, 88.5, 8.6, 0, "Eligible"],
        ["STU029", "Vicky K", "CSE", 6, 79.0, 7.3, 0, "Eligible"],
        ["STU030", "Katrina K", "IT", 6, 91.0, 8.9, 0, "Eligible"],
    ]
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    import_csv_to_sqlite(csv_file, db_file, table_name="students")
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
