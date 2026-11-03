import unittest
import json
import os
import re
import tempfile
from collections import Counter
from app import app
import database
from database import get_db_connection, init_db, record_test_result
from ml_engine import get_student_performance_data
from question_generator import DSA_APTITUDE_TOPICS, _shuffle_options

class TestLMS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def login_as(self, student_id, password):
        self.client.get('/logout')
        response = self.client.post('/login', data={'student_id': str(student_id), 'password': password})
        self.assertEqual(response.status_code, 302)

    def test_option_shuffle_preserves_correct_answer(self):
        options = ('first', 'second', 'third', 'fourth')
        for correct_index, answer in enumerate(('A', 'B', 'C', 'D')):
            shuffled, shuffled_answer = _shuffle_options(options, answer, f'prompt {answer}')
            self.assertEqual(set(shuffled), set(options))
            self.assertEqual(shuffled[ord(shuffled_answer) - ord('A')], options[correct_index])

    def test_home(self):
        self.login_as(1, 'rahul123')
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'HIGH SCHOOL STUDENTS', res.data)

    def test_highschool_routes(self):
        self.login_as(1, 'rahul123')
        routes = ['/highschool', '/highschool/test', '/highschool/games',
                  '/highschool/map-method', '/highschool/newspaper', '/highschool/performance']
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed")

    def test_puc_degree_routes(self):
        self.login_as(2, 'ananya123')
        routes = ['/puc-degree', '/puc-degree/test', '/puc-degree/performance']
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed")
        test_page = self.client.get('/puc-degree/test?subject=CET')
        self.assertIn(b'50 Unique Questions Each for Physics, Chemistry, and Mathematics', test_page.data)
        self.assertIn(b'count: 150', test_page.data)
        self.assertIn(b'Assessment Scores by Subject', res.data)
        self.assertNotIn(b'Accuracy Ratio', res.data)
        self.assertIn(b'<h5 class="fw-bold text-dark mb-3">JEE</h5>', res.data)

    def test_ml_explainability(self):
        self.login_as(1, 'rahul123')
        res = self.client.get('/ml-insights')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Empirical ML Model Evaluation & Explainability', res.data)
        self.assertIn(b'Confusion Matrix', res.data)

        metrics_res = self.client.get('/api/ml/metrics')
        self.assertEqual(metrics_res.status_code, 200)
        metrics = json.loads(metrics_res.data)
        self.assertIn('feature_importance', metrics)
        self.assertIn('confusion_matrix', metrics)

    def test_faculty_portal_removed(self):
        self.login_as(1, 'rahul123')
        dashboard = self.client.get('/')
        self.assertEqual(dashboard.status_code, 200)
        self.assertNotIn(b'Faculty Portal', dashboard.data)
        self.assertEqual(self.client.get('/teacher/dashboard').status_code, 404)
        self.assertEqual(self.client.get('/teacher/add-question').status_code, 404)

    def test_highschool_performance_download(self):
        self.login_as(1, 'rahul123')
        res = self.client.get('/highschool/performance/download')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.headers['Content-Type'].startswith('text/csv'))
        self.assertIn('high_school_performance_analysis.csv', res.headers['Content-Disposition'])
        self.assertIn(b'Summary Metric,Value', res.data)
        self.assertIn(b'Subject / Topic Breakdown', res.data)

    def test_puc_degree_performance_download(self):
        self.login_as(2, 'ananya123')
        res = self.client.get('/puc-degree/performance/download')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.headers['Content-Type'].startswith('text/csv'))
        self.assertIn('puc_degree_performance_analysis.csv', res.headers['Content-Disposition'])
        self.assertIn(b'Summary Metric,Value', res.data)
        self.assertIn(b'Test History', res.data)
        self.assertIn(b'CET Subject Scores', res.data)

    def test_performance_download_requires_login(self):
        self.client.get('/logout')
        res = self.client.get('/highschool/performance/download')
        self.assertEqual(res.status_code, 302)

    def test_highschool_50_questions_api(self):
        res = self.client.get('/api/questions?category=highschool&count=50')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['questions']), 50)
        allowed_subjects = {'Biology', 'Physics', 'Math', 'Chemistry', 'History', 'Geography', 'English'}
        returned_subjects = {q['subject'] for q in data['questions']}
        self.assertTrue(returned_subjects.issubset(allowed_subjects), f"Unexpected subjects in high school test: {returned_subjects}")
        # Verify 0 duplicates
        q_ids = [q['id'] for q in data['questions']]
        self.assertEqual(len(set(q_ids)), 50, "Duplicates found in High School test!")

    def test_puc_degree_default_questions_api(self):
        res = self.client.get('/api/questions?category=puc_degree')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['questions']), 50)
        # Verify 0 duplicates
        q_ids = [q['id'] for q in data['questions']]
        self.assertEqual(len(set(q_ids)), 50, "Duplicates found in PUC/Degree test!")

    def test_exam_question_banks_are_unique_and_have_no_indexed_prompts(self):
        highschool_res = self.client.get('/api/questions?category=highschool&count=50')
        highschool_questions = json.loads(highschool_res.data)['questions']
        highschool_text = {' '.join(q['question'].split()).casefold() for q in highschool_questions}
        self.assertEqual(len(highschool_text), len(highschool_questions))

        all_puc_text = set()
        correct_positions = set()
        for subject in ('CET', 'JEE', 'DSA Aptitude'):
            requested_count = 150 if subject in {'CET', 'JEE'} else 50
            response = self.client.get(
                f'/api/questions?category=puc_degree&subject={subject}&count={requested_count}'
            )
            self.assertEqual(response.status_code, 200)
            questions = json.loads(response.data)['questions']
            self.assertEqual(len(questions), requested_count, f'{subject} should contain {requested_count} questions')
            self.assertEqual(
                {question['exam'] for question in questions},
                {subject},
                f'{subject} questions should be tagged to their assessment'
            )
            if subject in {'CET', 'JEE'}:
                subject_counts = Counter(question['subject'] for question in questions)
                self.assertEqual(
                    subject_counts,
                    {'Physics': 50, 'Chemistry': 50, 'Mathematics': 50},
                    f'{subject} should contain 50 questions per subject'
                )
            else:
                topic_counts = Counter(question['topic'] for question in questions)
                self.assertEqual(
                    topic_counts,
                    {topic: 5 for topic in DSA_APTITUDE_TOPICS},
                    'DSA Aptitude should contain five unique questions for every requested topic'
                )
            normalized = {' '.join(q['question'].split()).casefold() for q in questions}
            self.assertEqual(len(normalized), requested_count, f'{subject} contains repeated question text')
            self.assertFalse(highschool_text & normalized, f'{subject} repeats a High School question')
            self.assertFalse(all_puc_text & normalized, f'{subject} repeats another PUC question')
            self.assertGreater(
                len({question['correct_answer'] for question in questions}),
                1,
                f'{subject} correct answers are not shuffled'
            )
            for question in questions:
                self.assertIn(question['correct_answer'], {'A', 'B', 'C', 'D'})
                correct_positions.add(question['correct_answer'])
                self.assertTrue(question[f"option_{question['correct_answer'].lower()}"])
                self.assertIsNone(
                    re.search(r'\b(?:question set|in question|in example|in trial)\s+\d+\b',
                              question['question'], re.IGNORECASE),
                    f'Question contains generated index text: {question["question"]}'
                )
            all_puc_text.update(normalized)
        self.assertGreater(len(correct_positions), 1, 'Correct answers should not all occupy the same option position')

    def test_cet_performance_includes_combined_subject_score(self):
        original_db_file = database.DB_FILE
        with tempfile.TemporaryDirectory() as temp_dir:
            database.DB_FILE = os.path.join(temp_dir, 'performance-test.db')
            try:
                init_db()
                conn = get_db_connection()
                question_ids = []
                for subject in ('Physics', 'Chemistry', 'Mathematics'):
                    cursor = conn.execute('''
                        INSERT INTO questions (
                            category, exam, subject, topic, question,
                            option_a, option_b, option_c, option_d, correct_answer, explanation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        'puc_degree', 'CET', subject, subject, f'Unique {subject} test prompt?',
                        'Correct', 'Wrong 1', 'Wrong 2', 'Wrong 3', 'A', 'Test explanation.'
                    ))
                    question_ids.append(cursor.lastrowid)
                conn.commit()
                conn.close()

                record_test_result(2, 'puc_degree', 'CET assessment', [
                    {
                        'question_id': question_id,
                        'selected_option': selected,
                        'correct_answer': 'A',
                    }
                    for question_id, selected in zip(question_ids, ('A', 'B', ''))
                ], exam='CET')

                cet = next(
                    assessment for assessment in get_student_performance_data(2, 'puc_degree')['assessment_breakdowns']
                    if assessment['exam'] == 'CET'
                )
                self.assertEqual(cet['total_correct'], 1)
                self.assertEqual(cet['total_asked'], 3)
                self.assertEqual(cet['percentage'], 33.3)
            finally:
                database.DB_FILE = original_db_file

    def test_jee_performance_omits_exam_name_as_extra_subject(self):
        original_db_file = database.DB_FILE
        with tempfile.TemporaryDirectory() as temp_dir:
            database.DB_FILE = os.path.join(temp_dir, 'jee-performance-test.db')
            try:
                init_db()
                conn = get_db_connection()
                question_ids = []
                for subject in ('Physics', 'Chemistry', 'Mathematics', 'JEE'):
                    cursor = conn.execute('''
                        INSERT INTO questions (
                            category, exam, subject, topic, question,
                            option_a, option_b, option_c, option_d, correct_answer, explanation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        'puc_degree', 'JEE', subject, subject, f'Unique JEE {subject} test prompt?',
                        'Correct', 'Wrong 1', 'Wrong 2', 'Wrong 3', 'A', 'Test explanation.'
                    ))
                    question_ids.append(cursor.lastrowid)
                conn.commit()
                conn.close()

                record_test_result(2, 'puc_degree', 'JEE assessment', [
                    {
                        'question_id': question_id,
                        'selected_option': 'A',
                        'correct_answer': 'A',
                    }
                    for question_id in question_ids
                ], exam='JEE')

                performance = get_student_performance_data(2, 'puc_degree')
                jee = next(
                    assessment for assessment in performance['assessment_breakdowns']
                    if assessment['exam'] == 'JEE'
                )
                self.assertEqual(
                    {item['subject'] for item in jee['subjects']},
                    {'Physics', 'Chemistry', 'Mathematics'}
                )
                self.assertEqual((jee['total_correct'], jee['total_asked']), (3, 3))
                self.assertFalse(any(item['subject'] == 'JEE' for item in performance['subject_breakdown']))
            finally:
                database.DB_FILE = original_db_file

    def test_submit_test(self):
        self.login_as(1, 'rahul123')
        sample_answers = [
            {"question_id": 1, "question_number": 1, "selected_option": "B", "correct_answer": "B"},
            {"question_id": 2, "question_number": 2, "selected_option": "C", "correct_answer": "C"},
            {"question_id": 3, "question_number": 3, "selected_option": "A", "correct_answer": "B"},
            {"question_id": 4, "question_number": 4, "selected_option": "NONE", "correct_answer": "C"}
        ]
        res = self.client.post('/api/submit-test',
                               data=json.dumps({"category": "highschool", "student_id": 1, "answers": sample_answers}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['result']['total_questions'], 4)
        self.assertEqual(data['result']['correct_answers'], 2)
        self.assertEqual(data['result']['incorrect_answers'], 1)
        self.assertEqual(data['result']['unattempted'], 1)
        self.assertEqual(data['result']['score'], 2)

    def test_save_game_score(self):
        self.login_as(1, 'rahul123')
        res = self.client.post('/api/save-game-score',
                               data=json.dumps({"category": "highschool", "student_id": 1, "game_type": "Biology Organs", "subject": "Biology", "score": 40, "max_score": 50}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')

    def test_map_generator_api(self):
        res = self.client.post('/api/generate-map',
                               data=json.dumps({"theory_text": "Step 1: Initiation. Step 2: Elongation. Step 3: Termination."}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn("graph TD", data['data']['diagram_code'])

    def test_summarizer_api(self):
        sample_article = """
        The Indian Space Research Organisation has made remarkable progress in lunar exploration.
        The Chandrayaan-3 mission landed near the South Pole of the moon.
        Scientific payloads detected significant chemical elements including sulfur and iron.
        Space agencies across the globe have congratulated the technological feat.
        """
        res = self.client.post('/api/summarize-news',
                               data=json.dumps({"text": sample_article}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(len(data['data']['summary']) > 0)
        self.assertTrue(len(data['data']['keywords']) > 0)

if __name__ == '__main__':
    unittest.main()
