import sqlite3
import os
import json
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lms.db')

def get_db_connection():
    """Establishes and returns a connection to SQLite with row dictionary factory."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes all necessary database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium'
        )
    ''')

    # 3. Tests table (Stores completed tests)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            test_title TEXT NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            incorrect_answers INTEGER NOT NULL,
            unattempted INTEGER NOT NULL,
            score INTEGER NOT NULL,
            percentage REAL NOT NULL,
            performance_level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # 4. Test Questions table (Stores exact questions and choices for an active or completed test)
    # Guaranteed NO duplicates per test session
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            selected_option TEXT,
            is_correct INTEGER DEFAULT 0,
            FOREIGN KEY (test_id) REFERENCES tests (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')

    # 5. Game Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            game_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            score INTEGER NOT NULL,
            max_score INTEGER NOT NULL,
            percentage REAL NOT NULL,
            time_taken_seconds INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # 6. Performance Analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            weak_topics TEXT,
            strong_topics TEXT,
            recommendation TEXT,
            predicted_level TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # Ensure default students exist
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO students (name, category) VALUES (?, ?)', ('Rahul Sharma (High School)', 'highschool'))
        cursor.execute('INSERT INTO students (name, category) VALUES (?, ?)', ('Ananya Verma (PUC & Degree)', 'puc_degree'))

    conn.commit()
    conn.close()
    print("Database initialized successfully with all tables.")

def get_or_create_default_student(category):
    """Retrieves default student ID for the selected category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM students WHERE category = ? ORDER BY id ASC LIMIT 1', (category,))
    row = cursor.fetchone()
    if row:
        student_id = row['id']
    else:
        name = "Student (" + category.title() + ")"
        cursor.execute('INSERT INTO students (name, category) VALUES (?, ?)', (name, category))
        conn.commit()
        student_id = cursor.lastrowid
    conn.close()
    return student_id

def fetch_unique_test_questions(category, count=50, subject=None):
    """
    Selects exactly `count` unique questions for a test session.
    Guarantees:
    - Never duplicates a question within the same test.
    - Balanced distribution across available subjects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if subject and subject != 'All':
        cursor.execute('''
            SELECT DISTINCT id, category, subject, topic, question, option_a, option_b, option_c, option_d,
                            correct_answer, explanation, difficulty
            FROM questions
            WHERE category = ? AND subject = ?
            ORDER BY RANDOM()
            LIMIT ?
        ''', (category, subject, count))
        questions = [dict(row) for row in cursor.fetchall()]
    else:
        # Fetch available subjects for balanced selection
        cursor.execute('SELECT DISTINCT subject FROM questions WHERE category = ?', (category,))
        subjects = [row['subject'] for row in cursor.fetchall()]

        questions = []
        seen_ids = set()

        if subjects:
            per_subj = max(1, count // len(subjects))
            for s in subjects:
                cursor.execute('''
                    SELECT id, category, subject, topic, question, option_a, option_b, option_c, option_d,
                           correct_answer, explanation, difficulty
                    FROM questions
                    WHERE category = ? AND subject = ?
                    ORDER BY RANDOM()
                    LIMIT ?
                ''', (category, s, per_subj))
                for row in cursor.fetchall():
                    if row['id'] not in seen_ids and len(questions) < count:
                        seen_ids.add(row['id'])
                        questions.append(dict(row))

        # If we still need more to reach exactly `count`, fetch remaining unique questions
        if len(questions) < count:
            needed = count - len(questions)
            if seen_ids:
                placeholders = ','.join('?' for _ in seen_ids)
                query = f'''
                    SELECT id, category, subject, topic, question, option_a, option_b, option_c, option_d,
                           correct_answer, explanation, difficulty
                    FROM questions
                    WHERE category = ? AND id NOT IN ({placeholders})
                    ORDER BY RANDOM()
                    LIMIT ?
                '''
                cursor.execute(query, [category] + list(seen_ids) + [needed])
            else:
                cursor.execute('''
                    SELECT id, category, subject, topic, question, option_a, option_b, option_c, option_d,
                           correct_answer, explanation, difficulty
                    FROM questions
                    WHERE category = ?
                    ORDER BY RANDOM()
                    LIMIT ?
                ''', (category, needed))

            for row in cursor.fetchall():
                if row['id'] not in seen_ids and len(questions) < count:
                    seen_ids.add(row['id'])
                    questions.append(dict(row))

    conn.close()

    # Double-check uniqueness constraint
    unique_check = set()
    sanitized_questions = []
    for q in questions:
        if q['id'] not in unique_check:
            unique_check.add(q['id'])
            sanitized_questions.append(q)

    return sanitized_questions

def record_test_result(student_id, category, test_title, answers_data):
    """
    Saves a completed test and all question responses to the database.
    answers_data: list of dicts with:
    { 'question_id': int, 'question_number': int, 'selected_option': str, 'correct_answer': str }
    """
    total = len(answers_data)
    correct = 0
    incorrect = 0
    unattempted = 0

    evaluated_details = []

    for item in answers_data:
        selected = (item.get('selected_option') or '').strip().upper()
        correct_opt = (item.get('correct_answer') or '').strip().upper()
        if not selected or selected == 'NONE':
            unattempted += 1
            is_corr = 0
        elif selected == correct_opt:
            correct += 1
            is_corr = 1
        else:
            incorrect += 1
            is_corr = 0

        evaluated_details.append({
            'question_id': item['question_id'],
            'question_number': item.get('question_number', 0),
            'selected_option': selected if selected else None,
            'is_correct': is_corr
        })

    score = correct
    percentage = round((correct / total * 100), 2) if total > 0 else 0.0

    if percentage >= 90:
        perf_level = "Excellent"
    elif percentage >= 75:
        perf_level = "Very Good"
    elif percentage >= 60:
        perf_level = "Good"
    elif percentage >= 40:
        perf_level = "Average"
    else:
        perf_level = "Needs Improvement"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tests (student_id, category, test_title, total_questions, correct_answers,
                           incorrect_answers, unattempted, score, percentage, performance_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, category, test_title, total, correct, incorrect, unattempted, score, percentage, perf_level))

    test_id = cursor.lastrowid

    for detail in evaluated_details:
        cursor.execute('''
            INSERT INTO test_questions (test_id, question_id, question_number, selected_option, is_correct)
            VALUES (?, ?, ?, ?, ?)
        ''', (test_id, detail['question_id'], detail['question_number'], detail['selected_option'], detail['is_correct']))

    conn.commit()
    conn.close()

    return {
        'test_id': test_id,
        'total_questions': total,
        'correct_answers': correct,
        'incorrect_answers': incorrect,
        'unattempted': unattempted,
        'score': score,
        'percentage': percentage,
        'performance_level': perf_level
    }

def record_game_score(student_id, game_type, subject, score, max_score, time_taken=0):
    """Records educational game result."""
    percentage = round((score / max_score * 100), 1) if max_score > 0 else 0
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_results (student_id, game_type, subject, score, max_score, percentage, time_taken_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, game_type, subject, score, max_score, percentage, time_taken))
    conn.commit()
    game_id = cursor.lastrowid
    conn.close()
    return game_id

if __name__ == '__main__':
    init_db()
