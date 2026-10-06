import json
from pathlib import Path
from app.services.mock_services import MockStudentRepository

def load_students(file_path: str, repository: MockStudentRepository):
    """
    Loads students from a JSON file into the repository.
    Example JSON format:
    [
        {"student_id": "S1001", "name": "Alice", "program": "CS", "attendance": {"CS201": "85%"}},
        {"student_id": "S1002", "name": "Bob", "program": "EE", "attendance": {"EE101": "90%"}}
    ]
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File {file_path} not found.")
        return
        
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    count = 0
    for student in data:
        student_id = student.get("student_id")
        if student_id:
            repository.upsert_student(student_id, student)
            count += 1
            
    print(f"Loaded {count} students into repository.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        repo = MockStudentRepository()
        load_students(sys.argv[1], repo)
        print("Final Repo State:", repo.db)
    else:
        print("Usage: python -m app.services.student_loader <path_to_json>")
