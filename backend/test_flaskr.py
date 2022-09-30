import os
from unicodedata import category
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

import os
username=os.getenv("USER_NAME")
password=os.getenv("PASSWORD")
ip_adresse=os.getenv("IP_ADRESSE")
port=os.getenv("PORT")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path ='postgresql://{}:{}@{}:{}/trivia'.format(username , password , ip_adresse , port)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        self.new_question ={
        "question":"who is the president of Guinea Conakry",
        "answer":"oumar doumbouya",
        "category":7,
        "difficulty":4
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_category(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(data['totals_categories']  , len(Category.query.all()))

    def test_get_all_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['totals_questions'] , len(Question.query.all()))


    def test_delete_question(self):
        id=6
        question=Question.query.filter(Question.id == id).one_or_none()
        res=self.client().delete(f'/api/questions/{id}')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)
        self.assertEqual(data['questions'] , question.format())
        self.assertEqual(data['totals_questions'] , len(Question.query.all()))

    def test_create_new_question(self):
        res=self.client().post('/api/questions', json = self.new_question)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['totals_questions'] , len(Question.query.all()))

    def test_get_question_search_with_result(self):
        res=self.client().post('/api/questions/search',json={'search_term':'which'})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['totals_questions'])
        self.assertTrue(data['questions'])




    def test_get_question_by_categorie(self):
        category = 2
        res=self.client().get(f'/api/questions/{category}')
        data=json.loads(res.data)
        plant=Question.query.filter(Question.category == category).all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['totals_questions'], len(plant))


    def test_get_quiz(self):
        res=self.client().post('/api/quiz', json = {"previous_id":23, "category":4})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totals_questions'])



    def test_404_requesting_over_the_value_page(self):
        res=self.client().get('/api/questions?page=1000')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_404_requesting_over_select_on_question(self):
        res=self.client().get('/api/question/whem')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')
    

    def test_404_requesting_delete_over_id_question(self):
        id=300
        question=Question.query.filter(Question.id == id).one_or_none()
        res=self.client().delete(f'/api/questions/{id}')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')


    def test_try_to_delete_with_post_metod(self):
        id=300
        question=Question.query.filter(Question.id == id).one_or_none()
        res=self.client().post(f'/api/questions/{id}')
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
    
    def test_500_create_new_question_with_unknown_category(self):
        res=self.client().post('/api/questions', json = {
        "question":"who is the president of Guinea Conakry",
        "answer":"oumar doumbouya",
        "category":9,
        "difficulty":4
        })
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'] , "internal server error")




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()