import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import config

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgresql://ali:hghghg@{}/{}".format('localhost:5432', self.database_name)
        self.database_path = config.test_database_path
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

    def test_get_categories(self):
        """ Gets all categories using /categories end point """
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))


    def test_get_questions(self):
        """ Gets all questions using /questions end point """
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_delete_question_existent(self):
        """ Existent question deletion """
        question = Question.query.order_by((Question.id)).first()
        self.assertNotEqual(question, None)

        question_id = str(question.id)

        res = self.client().delete(f'questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.get(int(question_id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_delete_question_inexistent(self):
        """ Inexistent question deletion """
        res = self.client().delete('/questions/55444444')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')


    def test_submit_question(self):
        """ Valid question submission """
        new_question = {
            'question': 'Question',
            'answer': 'Answer',
            'difficulty': 1,
            'category': int(2),
        }

        res = self.client().post('/questions/submit', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_submit_question_invalid(self):
        """ Invalid question submission """

        new_question = {
            'question': 'Question',
            'answer': 'Answer',
            'difficutly': 1,
            'invalid_field': 1,
        }

        res = self.client().post('/questions/submit', json=new_question)

        self.assertEqual(res.status_code, 422)


    def test_search_questions_valid(self):
        """ Valid question search """
        search_term = 'e'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))


    def test_search_questions_invalid(self):
        """ Invalid question search """
        search_term = 'asdasdasdsdadadsads'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})

        self.assertEqual(res.status_code, 404)


    def test_get_questions_by_category_valid(self):
        """ Valid category questions """
        id = int(2)
        res = self.client().get(f'/categories/{id}/questions')
        data = json.loads(res.data)
        message = 'res is {0} , data is {1}'

        self.assertEqual(res.status_code, 200, message.format(res, data))
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))




    def test_get_questions_by_category_invalid(self):
        """ Invalid category questios """
        id = int(50000000000)
        res = self.client().get(f'/categories/{id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        

    def test_play_quiz_all_categories(self):
        """ All categories quiz """

        res = self.client().get('/questions')
        data = json.loads(res.data)

        # Without a previous question 
        res = self.client().post('/quizzes/play', json={'previous_questions':[] , 'quiz_category':{'id':0}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        # With a previous question
        question = Question.query.first()
        res = self.client().post('/quizzes/play', json={'previous_questions':[question.id] , 'quiz_category':{'id':0}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


    def test_play_quiz_valid_category(self):
        """ Valid category quiz """

        res = self.client().get('/questions')
        data = json.loads(res.data)

        # Without a previous question 
        res = self.client().post('/quizzes/play', json={'previous_questions':[] , 'quiz_category':{'id':2}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        # With a previous question
        question = Question.query.first()
        res = self.client().post('/quizzes/play', json={'previous_questions':[question.id] , 'quiz_category':{'id':2}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


    def test_play_quiz_invalid_category(self):
        """ Invalid category quiz """

        res = self.client().get('/questions')
        data = json.loads(res.data)

        # Without a previous question 
        res = self.client().post('/quizzes/play', json={'previous_questions':[] , 'quiz_category':{'id':20000}})
        data = json.loads(res.data)
        self.assertFalse(data['question'])

        # With a previous question
        question = Question.query.first()
        res = self.client().post('/quizzes/play', json={'previous_questions':[question.id] , 'quiz_category':{'id':20000}})
        data = json.loads(res.data)
        self.assertFalse(data['question'])

        














        



    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()