import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category

load_dotenv()

DB_TEST_NAME = os.environ.get("DB_TEST_NAME")
DB_TEST_USER = os.environ.get("DB_TEST_USER")
DB_TEST_PASSWORD = os.environ.get("DB_TEST_PASSWORD")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(
            DB_TEST_USER, DB_TEST_PASSWORD, 'localhost:5432', DB_TEST_NAME)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Random question",
                             "answer": "Random answer", "difficulty": 4, "category": 2}
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/api/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data["categories"])

    def test_get_paginated_questions(self):
        res = self.client().get("/api/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data["categories"])
        self.assertIsNotNone(data["questions"])
        self.assertIsNotNone(data["totalQuestions"])

    def test_delete_question(self):
        res = self.client().delete("/api/questions/2")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)

    def test_delete_inexisting_question(self):
        res = self.client().delete("/api/questions/2475")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_create_new_question(self):
        res = self.client().post("/api/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_new_question_missing_data(self):
        res = self.client().post("/api/questions",
                                 json={"question": "Fine ?", "difficulty": 4})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_search_question(self):
        res = self.client().post("/api/questions/search",
                                 json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data["questions"])
        self.assertIsNotNone(data["totalQuestions"])

    def test_search_question_without_searchTerm(self):
        res = self.client().post("/api/questions/search", json={})
        data = json.loads(res.data)

    def test_get_next_question(self):
        res = self.client().post("/api/quizzes",
                                 json={"previous_questions": [1, 2], "quiz_category": {"id": 1, "type": "Science"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])

    def test_get_next_question_missing_category(self):
        res = self.client().post("/api/quizzes",
                                 json={"previous_questions": [1, 2]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)

    def test_get_questions_by_category(self):
        res = self.client().get("/api/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data["questions"])

    def test_get_questions_by_category_inexisting_category(self):
        res = self.client().get("/api/categories/24571/questions")
        self.assertEqual(res.status_code, 401)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
