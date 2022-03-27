import json
import os
from unicodedata import category
import unittest
from nis import cat

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import Category, Question, setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            
        self.test_question = Question(question="what's the value of 1+1?",
                                      answer='2',difficulty=1,category='1')
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_retrieve_categories_success(self):
        category = Category.query.first()
        response = self.client().get('/categories')
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['categories'][str(category.id)], category.type)
    
    def test_retrieve_categories_failure(self):
        Category.query.delete()
        response = self.client().get('/categories')
        json_data = response.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 404)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['message'], 'resource not found')

    def test_retrieve_questions_success(self):
        total_questions_num = Question.query.count()
        response = self.client().get('/questions?page=1')
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertTrue(json_data['categories'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['totalQuestions'], total_questions_num)
        self.assertEqual(len(json_data['questions']), min(10, total_questions_num))

    def test_retrieve_questions_failure_1(self):
        response = self.client().get('/questions?page=1000000000')
        json_data = response.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 404)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['message'], 'resource not found')

    def test_retrieve_questions_failure_2(self):
        Category.query.delete()
        response = self.client().get('/questions?page=1')
        json_data = response.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 404)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['message'], 'resource not found')

    def test_delete_question_by_id_success(self):
        self.test_question.insert()
        test_question_id = self.test_question.id
        response = self.client().delete(f'/questions/{test_question_id}')
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['id'], test_question_id)
        self.assertIsNone(Question.query.get(test_question_id))
        
    def test_delete_question_by_id_failure(self):
        response = self.client().delete('/questions/1000000000')
        json_data = response.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 422)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(json_data['message'], 'unprocessable')
        
    def test_search_questions_success(self):
        self.test_question.insert()
        response = self.client().post('/questions', json={'searchTerm': 'value'})
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(json_data['questions']), 1)
        self.assertEqual(json_data['total_questions'], len(json_data['questions']))
        self.test_question.delete()
        
    def test_search_questions_failure(self):
        Question.query.filter(Question.question.ilike('%'+'s0meth1ngn0tex1st'+'%')).delete(synchronize_session=False)
        response = self.client().post('/questions', json={'searchTerm': 's0meth1ngn0tex1st'})
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_data['questions']), 0)
        self.assertEqual(json_data['total_questions'], 0)

    def test_create_question_success(self):
        Question.query.filter_by(question="what's the value of 1+1?").delete()
        response = self.client().post('/questions', json=self.test_question.format())
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.query.filter_by(question="what's the value of 1+1?").count(), 1)
        
    def test_create_question_failure(self):
        response = self.client().post('/questions', json={'x':'y'})
        json_data = response.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_data['message'], 'bad request')
        
    def test_retrieve_questions_by_category_success(self):
        response = self.client().get('/categories/1/questions')
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['totalQuestions'], Question.query.filter_by(category=1).count())
        self.assertEqual(json_data['currentCategory'], Category.query.get(1).type)
        
    def test_retrieve_questions_by_category_failure(self):
        response = self.client().get('/categories/1000000000/questions')
        json_data = response.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 404)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data['message'], 'resource not found')
        
    def test_retrieve_quiz_question_success(self):
        previous_question_id = Question.query.filter_by(category=2).first().id
        response = self.client().post('/quizzes', json={'previous_questions': [previous_question_id],
                              'quiz_category': Category.query.get(2).format()})
        json_data = response.get_json()
        self.assertTrue(json_data['success'])
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(json_data), 2)
        if 'question' in json_data:
            self.assertNotEqual(json_data['question']['id'], previous_question_id)

    def test_retrieve_quiz_question_failure(self):
        response = self.client().post('/quizzes', json={'x': 'y'})
        json_data = response.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['error'], 400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_data['message'], 'bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
