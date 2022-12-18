import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'postgres', 'password1', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_fetch_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertTrue(len(data["categories"]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_fetch_questions(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question(self):
        question = Question(
            question="test question",
            answer="test answer",
            difficulty=1,
            category=4)
        question.insert()

        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_question(self):
        res = self.client().post(
            "/questions",
            json={
                "question": "test question",
                "answer": "test answer",
                "difficulty": 1,
                "category": 4})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_questions(self):
        res = self.client().post(
            "/questions/search",
            json={
                "searchTerm": "Africa"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_fetch_questions_by_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_fetch_quizzes(self):
        previous_questions = [1, 4, 20, 15]
        quiz_category = {'id': 1, 'type': "Science"}

        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": previous_questions,
                'quiz_category': quiz_category})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data["success"], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
