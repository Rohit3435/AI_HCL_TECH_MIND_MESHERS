"""Deterministic tools for querying structured student data from SQLite."""

from tools.student_tools import (
    get_student_details,
    get_student_attendance,
    get_student_cgpa,
    get_student_backlogs,
    get_student_eligibility_status,
    list_students,
)

__all__ = [
    "get_student_details",
    "get_student_attendance",
    "get_student_cgpa",
    "get_student_backlogs",
    "get_student_eligibility_status",
    "list_students",
]
