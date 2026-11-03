import sqlite3
import os
import json
from collections import Counter
from werkzeug.security import check_password_hash, generate_password_hash
from question_generator import (
    DSA_APTITUDE_TOPICS,
    generate_additional_questions,
    _shuffle_options,
)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lms.db')
HIGH_SCHOOL_ALLOWED_SUBJECTS = (
    'Biology',
    'Physics',
    'Math',
    'Chemistry',
    'History',
    'Geography',
    'English',
)
PUC_EXAM_SUBJECTS = ('CET', 'JEE', 'DSA Aptitude')
DSA_TOPIC_ALIASES = {
    'hashing': 'Hash Maps',
    'array complexity': 'Arrays',
    'binary trees': 'Trees',
    'binary search': 'Searching',
}


def _canonical_dsa_topic(value):
    """Maps legacy DSA labels to the current assessment topic names."""
    normalized = ' '.join((value or '').split()).casefold()
    if normalized in DSA_TOPIC_ALIASES:
        return DSA_TOPIC_ALIASES[normalized]
    return next((topic for topic in DSA_APTITUDE_TOPICS if topic.casefold() == normalized), None)

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
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    student_columns = [row['name'] for row in cursor.execute('PRAGMA table_info(students)').fetchall()]
    if 'password_hash' not in student_columns:
        cursor.execute('ALTER TABLE students ADD COLUMN password_hash TEXT')
    if 'role' not in student_columns:
        cursor.execute("ALTER TABLE students ADD COLUMN role TEXT DEFAULT 'student'")

    # 2. Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            exam TEXT,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium',
            is_active INTEGER NOT NULL DEFAULT 1
        )
    ''')
    question_columns = [row['name'] for row in cursor.execute('PRAGMA table_info(questions)').fetchall()]
    if 'is_active' not in question_columns:
        cursor.execute('ALTER TABLE questions ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1')
    if 'exam' not in question_columns:
        cursor.execute('ALTER TABLE questions ADD COLUMN exam TEXT')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_migrations (
            name TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    legacy_question_migration = 'replace-repeated-question-templates'
    migration_applied = cursor.execute(
        'SELECT 1 FROM app_migrations WHERE name = ?', (legacy_question_migration,)
    ).fetchone()
    if not migration_applied:
        cursor.execute('''
            UPDATE questions
            SET is_active = 0
            WHERE (category = 'puc_degree' AND subject IN ('CET', 'JEE', 'DSA Aptitude'))
               OR (LOWER(question) LIKE '%question set %'
                   OR LOWER(question) LIKE '%in question %'
                   OR LOWER(question) LIKE '%in example %'
                   OR LOWER(question) LIKE '%in trial %'
                   OR LOWER(question) LIKE '%expression %?'
                   OR LOWER(question) LIKE 'what is the time complexity of scanning an array of % elements once%'
                   OR LOWER(question) LIKE 'how many indices does a zero-based array containing % items have?'
                   OR LOWER(question) LIKE 'what is % + %?'
                   OR LOWER(question) LIKE 'what is % - %?'
                   OR LOWER(question) LIKE 'how many metres are equal to % kilometres?')
        ''')
        cursor.execute(
            'INSERT INTO app_migrations (name) VALUES (?)',
            (legacy_question_migration,)
        )

    option_shuffle_migration = 'shuffle-puc-exam-answer-options'
    if not cursor.execute(
        'SELECT 1 FROM app_migrations WHERE name = ?', (option_shuffle_migration,)
    ).fetchone():
        cursor.execute('''
            SELECT id, question, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE category = 'puc_degree' AND exam IN ('CET', 'JEE', 'DSA Aptitude')
              AND is_active = 1
        ''')
        for row in cursor.fetchall():
            options, answer = _shuffle_options(
                (row['option_a'], row['option_b'], row['option_c'], row['option_d']),
                row['correct_answer'],
                row['question'],
            )
            cursor.execute('''
                UPDATE questions
                SET option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_answer = ?
                WHERE id = ?
            ''', (*options, answer, row['id']))
        cursor.execute(
            'INSERT INTO app_migrations (name) VALUES (?)',
            (option_shuffle_migration,)
        )

    dsa_topic_migration = 'standardize-dsa-assessment-topics'
    if not cursor.execute(
        'SELECT 1 FROM app_migrations WHERE name = ?', (dsa_topic_migration,)
    ).fetchone():
        cursor.execute('''
            SELECT id, subject, topic
            FROM questions
            WHERE category = 'puc_degree' AND exam = 'DSA Aptitude'
        ''')
        for row in cursor.fetchall():
            canonical_topic = (
                _canonical_dsa_topic(row['topic'])
                or _canonical_dsa_topic(row['subject'])
            )
            if canonical_topic:
                cursor.execute('''
                    UPDATE questions
                    SET subject = ?, topic = ?
                    WHERE id = ?
                ''', (canonical_topic, canonical_topic, row['id']))
        cursor.execute(
            'INSERT INTO app_migrations (name) VALUES (?)',
            (dsa_topic_migration,)
        )

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
    test_columns = [row['name'] for row in cursor.execute('PRAGMA table_info(tests)').fetchall()]
    if 'exam' not in test_columns:
        cursor.execute('ALTER TABLE tests ADD COLUMN exam TEXT')

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
        cursor.execute(
            'INSERT INTO students (name, category, password_hash) VALUES (?, ?, ?)',
            ('Rahul Sharma (High School)', 'highschool', generate_password_hash('rahul123'))
        )
        cursor.execute(
            'INSERT INTO students (name, category, password_hash) VALUES (?, ?, ?)',
            ('Ananya Verma (PUC & Degree)', 'puc_degree', generate_password_hash('ananya123'))
        )

    default_passwords = {
        'Rahul Sharma (High School)': 'rahul123',
        'Ananya Verma (PUC & Degree)': 'ananya123'
    }
    for name, password in default_passwords.items():
        cursor.execute(
            'UPDATE students SET password_hash = ?, role = ? WHERE name = ? AND (password_hash IS NULL OR role IS NULL)',
            (generate_password_hash(password), 'student', name)
        )

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

def get_student_profile(student_id):
    """Returns the student identity record used by the learning modules."""
    conn = get_db_connection()
    row = conn.execute(
        'SELECT id, name, category, COALESCE(role, "student") as role, created_at FROM students WHERE id = ? AND COALESCE(role, "student") = "student"',
        (student_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def authenticate_student(student_id, password):
    """Returns a student profile when the ID and password are valid."""
    conn = get_db_connection()
    row = conn.execute(
        'SELECT id, name, category, COALESCE(role, "student") as role, password_hash, created_at FROM students WHERE id = ? AND COALESCE(role, "student") = "student"',
        (student_id,)
    ).fetchone()
    conn.close()
    if not row or not row['password_hash'] or not check_password_hash(row['password_hash'], password):
        return None
    profile = dict(row)
    profile.pop('password_hash', None)
    return profile

def create_student(name, category, password):
    """Creates a student account and returns its generated ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO students (name, category, password_hash, role) VALUES (?, ?, ?, ?)',
        (name.strip(), category, generate_password_hash(password), 'student')
    )
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return student_id

def fetch_unique_test_questions(category, count=50, subject=None):
    """
    Selects exactly `count` unique questions for a test session.
    Guarantees:
    - Never duplicates a question within the same test.
    - CET and JEE contain 50 questions in each of Physics, Chemistry, and Mathematics.
    - Balanced distribution across the allowed high-school subjects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    general_puc_test = category == 'puc_degree' and (not subject or subject == 'All')

    if count > 0:
        if category == 'highschool' and (not subject or subject == 'All'):
            placeholders = ', '.join('?' for _ in HIGH_SCHOOL_ALLOWED_SUBJECTS)
            cursor.execute(
                f'SELECT * FROM questions WHERE category = ? AND subject IN ({placeholders}) AND is_active = 1',
                (category, *HIGH_SCHOOL_ALLOWED_SUBJECTS)
            )
        elif general_puc_test:
            cursor.execute(
                'SELECT * FROM questions WHERE category = ? AND exam IS NULL AND is_active = 1',
                (category,)
            )
        elif category == 'puc_degree' and subject in PUC_EXAM_SUBJECTS:
            cursor.execute(
                'SELECT * FROM questions WHERE category = ? AND exam = ? AND is_active = 1',
                (category, subject)
            )
        elif subject and subject != 'All':
            cursor.execute('SELECT * FROM questions WHERE category = ? AND subject = ? AND is_active = 1', (category, subject))
        else:
            cursor.execute('SELECT * FROM questions WHERE category = ? AND is_active = 1', (category,))
        existing_questions = [dict(row) for row in cursor.fetchall()]
        exam_subjects = ('Physics', 'Chemistry', 'Mathematics') if (
            category == 'puc_degree' and subject in {'CET', 'JEE'}
        ) else ()
        subject_counts = Counter(row['subject'] for row in existing_questions)
        required_subject_counts = None
        required_topic_counts = None
        if exam_subjects:
            required_subject_counts = {
                section: max(0, 50 - subject_counts[section])
                for section in exam_subjects
            }
            section_shortfall = sum(required_subject_counts.values())
        elif category == 'puc_degree' and subject == 'DSA Aptitude':
            topic_counts = Counter(
                _canonical_dsa_topic(row.get('topic')) or _canonical_dsa_topic(row.get('subject'))
                for row in existing_questions
            )
            required_topic_counts = {
                topic: max(0, 5 - topic_counts[topic])
                for topic in DSA_APTITUDE_TOPICS
            }
            section_shortfall = sum(required_topic_counts.values())
        else:
            section_shortfall = 0
        questions_needed = max(count - len(existing_questions), section_shortfall)
        if questions_needed > 0:
            if category == 'puc_degree' and subject in PUC_EXAM_SUBJECTS:
                cursor.execute('SELECT question FROM questions')
            elif subject and subject != 'All':
                cursor.execute('''
                    SELECT question FROM questions
                    WHERE NOT (category = ? AND subject = ?)
                ''', (category, subject))
            elif general_puc_test:
                cursor.execute(
                    'SELECT question FROM questions WHERE category != ? OR exam IS NOT NULL',
                    (category,)
                )
            else:
                cursor.execute(
                    'SELECT question FROM questions WHERE category != ?',
                    (category,)
                )
            other_category_questions = [
                {'question': row['question']} for row in cursor.fetchall()
            ]
            generation_pool = existing_questions + other_category_questions
            generation_target = len(generation_pool) + questions_needed
            additions = generate_additional_questions(
                category,
                generation_pool,
                generation_target,
                subject=subject,
                required_subject_counts=required_subject_counts,
                required_topic_counts=required_topic_counts,
            )
            for question in additions:
                cursor.execute('''
                    INSERT INTO questions (category, exam, subject, topic, question, option_a, option_b,
                                           option_c, option_d, correct_answer, explanation, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (question['category'], question.get('exam'), question['subject'], question['topic'], question['question'],
                      question['option_a'], question['option_b'], question['option_c'], question['option_d'],
                      question['correct_answer'], question['explanation'], question['difficulty']))
            conn.commit()

    if category == 'highschool':
        allowed_subjects = HIGH_SCHOOL_ALLOWED_SUBJECTS
        if subject and subject != 'All':
            subject_values = (subject,) if subject in allowed_subjects else ()
        else:
            subject_values = allowed_subjects
    else:
        subject_values = ()

    if category == 'highschool' and subject_values:
        placeholders = ', '.join('?' for _ in subject_values)
        if subject and subject != 'All':
            cursor.execute('''
                SELECT DISTINCT id, category, exam, subject, topic, question, option_a, option_b, option_c, option_d,
                                correct_answer, explanation, difficulty
                FROM questions
                WHERE category = ? AND subject = ? AND is_active = 1
                ORDER BY RANDOM()
                LIMIT ?
            ''', (category, subject, count))
            questions = [dict(row) for row in cursor.fetchall()]
        else:
            cursor.execute(f'''
                SELECT DISTINCT id, category, exam, subject, topic, question, option_a, option_b, option_c, option_d,
                                correct_answer, explanation, difficulty
                FROM questions
                WHERE category = ? AND subject IN ({placeholders}) AND is_active = 1
                ORDER BY RANDOM()
            ''', (category, *subject_values))
            all_rows = [dict(row) for row in cursor.fetchall()]
            questions = []
            seen_ids = set()
            for row in all_rows:
                if row['id'] not in seen_ids and len(questions) < count:
                    seen_ids.add(row['id'])
                    questions.append(row)
    else:
        if category == 'puc_degree' and subject in PUC_EXAM_SUBJECTS:
            cursor.execute('''
                SELECT DISTINCT id, category, exam, subject, topic, question, option_a, option_b, option_c, option_d,
                                correct_answer, explanation, difficulty
                FROM questions
                WHERE category = ? AND exam = ? AND is_active = 1
                ORDER BY RANDOM()
            ''', (category, subject))
            buckets = {}
            for row in cursor.fetchall():
                item = dict(row)
                buckets.setdefault(item['subject'], []).append(item)

            questions = []
            if subject in {'CET', 'JEE'}:
                for question_subject in ('Physics', 'Chemistry', 'Mathematics'):
                    unique_text = set()
                    selected = []
                    for question in buckets.get(question_subject, []):
                        normalized_text = ' '.join(question['question'].split()).casefold()
                        if normalized_text not in unique_text:
                            unique_text.add(normalized_text)
                            selected.append(question)
                        if len(selected) == 50:
                            break
                    if len(selected) < 50:
                        conn.close()
                        raise RuntimeError(
                            f'{subject} question bank has only {len(selected)} unique '
                            f'{question_subject} questions; 50 are required.'
                        )
                    questions.extend(selected)
            elif subject == 'DSA Aptitude':
                unique_text = set()
                for topic in DSA_APTITUDE_TOPICS:
                    selected = []
                    for question in buckets.get(topic, []):
                        normalized_text = ' '.join(question['question'].split()).casefold()
                        if normalized_text in unique_text:
                            continue
                        unique_text.add(normalized_text)
                        selected.append(question)
                        if len(selected) == 5:
                            break
                    if len(selected) < 5:
                        conn.close()
                        raise RuntimeError(
                            f'DSA Aptitude question bank has only {len(selected)} unique '
                            f'{topic} questions; 5 are required.'
                        )
                    questions.extend(selected)
            else:
                subject_order = sorted(buckets)
                while len(questions) < count and any(buckets.values()):
                    for question_subject in subject_order:
                        if buckets[question_subject] and len(questions) < count:
                            questions.append(buckets[question_subject].pop())
        elif subject and subject != 'All':
            cursor.execute('''
                SELECT DISTINCT id, category, exam, subject, topic, question, option_a, option_b, option_c, option_d,
                                correct_answer, explanation, difficulty
                FROM questions
                WHERE category = ? AND subject = ? AND is_active = 1
                ORDER BY RANDOM()
                LIMIT ?
            ''', (category, subject, count))
            questions = [dict(row) for row in cursor.fetchall()]
        else:
            if general_puc_test:
                cursor.execute(
                    '''SELECT DISTINCT subject FROM questions
                       WHERE category = ? AND exam IS NULL AND is_active = 1''',
                    (category,)
                )
            else:
                cursor.execute(
                    'SELECT DISTINCT subject FROM questions WHERE category = ? AND is_active = 1',
                    (category,)
                )
            subjects = [row['subject'] for row in cursor.fetchall()]

            questions = []
            seen_ids = set()

            if subjects:
                per_subj = max(1, count // len(subjects))
                for s in subjects:
                    cursor.execute(f'''
                        SELECT id, category, exam, subject, topic, question, option_a, option_b, option_c, option_d,
                               correct_answer, explanation, difficulty
                        FROM questions
                        WHERE category = ? AND subject = ? AND is_active = 1
                        {'AND exam IS NULL' if general_puc_test else ''}
                        ORDER BY RANDOM()
                        LIMIT ?
                    ''', (category, s, per_subj))
                    for row in cursor.fetchall():
                        if row['id'] not in seen_ids and len(questions) < count:
                            seen_ids.add(row['id'])
                            questions.append(dict(row))

            if len(questions) < count:
                needed = count - len(questions)
                if seen_ids:
                    placeholders = ','.join('?' for _ in seen_ids)
                    query = f'''
                        SELECT id, category, exam, subject, topic, question, option_a, option_b, option_c, option_d,
                               correct_answer, explanation, difficulty
                        FROM questions
                        WHERE category = ? AND id NOT IN ({placeholders}) AND is_active = 1
                        {'AND exam IS NULL' if general_puc_test else ''}
                        ORDER BY RANDOM()
                        LIMIT ?
                    '''
                    params = [category] + list(seen_ids)
                    params.append(needed)
                    cursor.execute(query, params)
                else:
                    query = f'''
                        SELECT id, category, exam, subject, topic, question, option_a, option_b, option_c, option_d,
                               correct_answer, explanation, difficulty
                        FROM questions
                        WHERE category = ? AND is_active = 1
                        {'AND exam IS NULL' if general_puc_test else ''}
                        ORDER BY RANDOM()
                        LIMIT ?
                    '''
                    params = [category]
                    params.append(needed)
                    cursor.execute(query, params)

                for row in cursor.fetchall():
                    if row['id'] not in seen_ids and len(questions) < count:
                        seen_ids.add(row['id'])
                        questions.append(dict(row))

    conn.close()

    # Double-check uniqueness constraint
    unique_check = set()
    question_text_check = set()
    sanitized_questions = []
    for q in questions:
        question_text = ' '.join(q['question'].split()).casefold()
        if q['id'] not in unique_check and question_text not in question_text_check:
            unique_check.add(q['id'])
            question_text_check.add(question_text)
            sanitized_questions.append(q)

    return sanitized_questions

def record_test_result(student_id, category, test_title, answers_data, exam=None):
    """
    Saves a test session and its responses for historical performance tracking.
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
                           incorrect_answers, unattempted, score, percentage, performance_level, exam)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, category, test_title, total, correct, incorrect, unattempted, score, percentage, perf_level, exam))

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
