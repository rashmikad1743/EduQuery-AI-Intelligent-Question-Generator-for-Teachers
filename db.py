# db.py
import sqlite3
from typing import List, Dict, Any

# Default database path
DB_PATH = "questions.db"

# SQL for table creation
CREATE_SQL = '''
CREATE TABLE IF NOT EXISTS generated_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    question_type TEXT,
    question_text TEXT,
    choices TEXT,
    answer TEXT,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
'''


def init_db(path: str = DB_PATH):
    """Initialize the database and create the table if not exists."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(CREATE_SQL)
    conn.commit()
    conn.close()


def save_question(source: str, question_type: str, question_text: str,
                  choices: str, answer: str, metadata: str,
                  path: str = DB_PATH):
    """Insert a generated question into the database."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO generated_questions 
        (source, question_type, question_text, choices, answer, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (source, question_type, question_text, choices, answer, metadata))
    conn.commit()
    conn.close()


def list_questions(path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Fetch all questions from the database."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = c.execute(
        'SELECT * FROM generated_questions ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
