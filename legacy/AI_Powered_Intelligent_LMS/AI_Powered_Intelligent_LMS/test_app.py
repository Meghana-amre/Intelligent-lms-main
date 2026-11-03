import unittest
import json
from app import app
from database import init_db

class TestLMS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_home(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'HIGH SCHOOL STUDENTS', res.data)
        self.assertIn(b'PUC & DEGREE STUDENTS', res.data)

    def test_highschool_routes(self):
        routes = ['/highschool', '/highschool/test', '/highschool/games',
                  '/highschool/map-method', '/highschool/newspaper', '/highschool/performance']
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed")

    def test_puc_degree_routes(self):
        routes = ['/puc-degree', '/puc-degree/test', '/puc-degree/performance']
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed")

    def test_highschool_50_questions_api(self):
        res = self.client.get('/api/questions?category=highschool&count=50')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['questions']), 50)
        # Verify 0 duplicates
        q_ids = [q['id'] for q in data['questions']]
        self.assertEqual(len(set(q_ids)), 50, "Duplicates found in High School test!")

    def test_puc_degree_100_questions_api(self):
        res = self.client.get('/api/questions?category=puc_degree&count=100')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['questions']), 100)
        # Verify 0 duplicates
        q_ids = [q['id'] for q in data['questions']]
        self.assertEqual(len(set(q_ids)), 100, "Duplicates found in PUC/Degree test!")

    def test_submit_test(self):
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
