"""Deterministic SQL tools for querying verified student data from SQLite."""

from pathlib import Path
from typing import Any

from database.connection import DEFAULT_DB_PATH, fetch_all, fetch_one


def _format_response(
    student_id: str,
    data: dict[str, Any] | None,
    table_name: str = "students",
) -> dict[str, Any]:
    """Format a consistent structured tool response."""
    if data is None:
        return {
            "status": "NOT_FOUND",
            "student_id": student_id,
            "data": None,
            "source": f"sqlite:{table_name}",
        }
    return {
        "status": "FOUND",
        "student_id": student_id,
        "data": data,
        "source": f"sqlite:{table_name}",
    }


def get_student_details(
    student_id: str, db_path: str | Path = DEFAULT_DB_PATH
) -> dict[str, Any]:
    """Retrieve full profile details for a verified student.

    SQL query is strictly parameterized to prevent SQL injection and ensure
    deterministic lookup.
    """
    cleaned_id = str(student_id).strip()
    query = """
    SELECT student_id, name, branch, semester, attendance_percent, cgpa, backlogs, attendance_status
    FROM students
    WHERE UPPER(student_id) = UPPER(?);
    """
    row = fetch_one(query, (cleaned_id,), db_path=db_path)
    return _format_response(cleaned_id, row)


def get_student_by_name(
    name: str, db_path: str | Path = DEFAULT_DB_PATH
) -> dict[str, Any]:
    """Look up a student profile and email by their name."""
    cleaned_name = str(name).strip()
    query = """
    SELECT student_id, name, branch, semester, attendance_percent, cgpa, backlogs, attendance_status
    FROM students
    WHERE LOWER(name) LIKE LOWER(?);
    """
    row = fetch_one(query, (f"%{cleaned_name}%",), db_path=db_path)
    if row:
        try:
            user_row = fetch_one(
                "SELECT email FROM users WHERE UPPER(student_id) = UPPER(?);",
                (row["student_id"],),
                db_path=db_path,
            )
            if user_row:
                row["email"] = user_row["email"]
        except Exception:
            pass
    student_id = row["student_id"] if row else cleaned_name
    return _format_response(student_id, row)




def get_student_attendance(
    student_id: str, db_path: str | Path = DEFAULT_DB_PATH
) -> dict[str, Any]:
    """Retrieve attendance metrics and eligibility status for a verified student."""
    cleaned_id = str(student_id).strip()
    query = """
    SELECT student_id, name, attendance_percent, attendance_status
    FROM students
    WHERE UPPER(student_id) = UPPER(?);
    """
    row = fetch_one(query, (cleaned_id,), db_path=db_path)
    return _format_response(cleaned_id, row)


def get_student_cgpa(
    student_id: str, db_path: str | Path = DEFAULT_DB_PATH
) -> dict[str, Any]:
    """Retrieve CGPA and academic standing for a verified student."""
    cleaned_id = str(student_id).strip()
    query = """
    SELECT student_id, name, branch, semester, cgpa
    FROM students
    WHERE UPPER(student_id) = UPPER(?);
    """
    row = fetch_one(query, (cleaned_id,), db_path=db_path)
    return _format_response(cleaned_id, row)


def get_student_backlogs(
    student_id: str, db_path: str | Path = DEFAULT_DB_PATH
) -> dict[str, Any]:
    """Retrieve backlog count for a verified student."""
    cleaned_id = str(student_id).strip()
    query = """
    SELECT student_id, name, backlogs
    FROM students
    WHERE UPPER(student_id) = UPPER(?);
    """
    row = fetch_one(query, (cleaned_id,), db_path=db_path)
    return _format_response(cleaned_id, row)


def get_student_eligibility_status(
    student_id: str, db_path: str | Path = DEFAULT_DB_PATH
) -> dict[str, Any]:
    """Retrieve attendance eligibility status for exam/placements."""
    cleaned_id = str(student_id).strip()
    query = """
    SELECT student_id, name, attendance_percent, attendance_status, backlogs
    FROM students
    WHERE UPPER(student_id) = UPPER(?);
    """
    row = fetch_one(query, (cleaned_id,), db_path=db_path)
    return _format_response(cleaned_id, row)


def list_students(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Retrieve all student summary records (for administrative overview)."""
    query = """
    SELECT student_id, name, branch, semester, attendance_percent, cgpa, backlogs, attendance_status
    FROM students
    ORDER BY student_id ASC;
    """
    return fetch_all(query, (), db_path=db_path)


def verify_student_login(
    email: str,
    password: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Verify student login credentials against the users table."""
    cleaned_email = str(email).strip().lower()
    cleaned_pwd = str(password).strip()

    query = """
    SELECT student_id, student_name, email
    FROM users
    WHERE LOWER(email) = ? AND password = ?;
    """
    row = fetch_one(query, (cleaned_email, cleaned_pwd), db_path=db_path)
    if row is None:
        return {
            "status": "UNAUTHORIZED",
            "authenticated": False,
            "user": None,
            "source": "sqlite:users",
        }
    return {
        "status": "AUTHENTICATED",
        "authenticated": True,
        "user": row,
        "source": "sqlite:users",
    }


def get_student_user_profile(
    student_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Retrieve user credentials profile by student ID."""
    cleaned_id = str(student_id).strip()
    query = """
    SELECT student_id, student_name, email
    FROM users
    WHERE UPPER(student_id) = UPPER(?);
    """
    row = fetch_one(query, (cleaned_id,), db_path=db_path)
    return _format_response(cleaned_id, row, table_name="users")

