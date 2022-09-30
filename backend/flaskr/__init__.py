from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func, null , or_
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_plants(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    plants = [plant.format() for plant in selection]
    current_plants = plants[start:end]
    return current_plants

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app)
    # cors=CORS(app=app , resources={r"/api/*":{"origins":'*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow(valider)
    """
    @app.after_request
    def after_request(response):
        # response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,PUT,POST,DELETE,OPTIONS')
        return response


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.(valider)
    """
    @app.route('/api/categories')
    def get_categories():
        categories = Category.query.all()
        current_categories = paginate_plants(request, categories)
        if len(current_categories) == 0:
            abort(404)
        else:
            current_questions = current_categories
            return jsonify({
                'success': True,
                'categories': { value.id : value.type for value in Category.query.all()},
                'totals_categories': len(categories)
            })



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.(valider)

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/api/questions')
    def get_questions():
        questions = Question.query.all()
        current_questions = paginate_plants(request, questions)
        if len(current_questions) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'categories': { value.id : value.type for value in Category.query.all()} , 
                "current_category": [ (Category.query.filter_by(id=value["category"]).first()).type  for value in current_questions ], 
                'totals_questions': len(questions)
            })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.(valider)

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/api/questions/<int:id_question>' , methods=['DELETE'])
    def delete_questions(id_question):
        question= Question.query.filter_by(id=id_question).one_or_none()
        if question is None:
            abort(404)
        else:
            question.delete()
            return jsonify({
                'success': True,
                'deleted':id_question,
                'questions': question.format(),
                'totals_questions': len(Question.query.all())
            })
    

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.(valider)

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/api/questions' , methods=['POST'])
    def post_questions():

        body = request.get_json() 
        if body.get('question', None) is None or body.get('answer', None) is None or body.get('category', None) is None or body.get('difficulty', None) is None:
            abort(400)
        else:
            cat = Category.query.filter_by(id=body.get('category')).one_or_none
            if cat is None :
                abort(404)
            else :
                try:
                    question=Question(
                    question= body.get('question', None),
                    answer = body.get('answer', None),
                    category = body.get('category', None),
                    difficulty = body.get('difficulty', None))
                    question.insert()
                    return jsonify({
                        'success': True,
                        'created': question.id ,
                        'questions': question.format(),
                        'totals_questions': len(Question.query.all())
                    })
                except:
                    abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.(valider)

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/api/search/questions' , methods=['POST'])
    def search_questions():
        body = request.get_json() 
        if body.get('search_term', None) is None:
            abort(404)
        else:
            questions=Question.query.filter(or_(func.lower(Question.question).like('%' +body.get('search_term').lower()+ '%') , func.lower(Question.answer).like('%' +body.get('search_term').lower()+ '%'))).all()
            if len(questions) == 0 : 
                abort(404)
            else:
                current_questions = paginate_plants(request, questions)
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'current_category': [ (Category.query.filter_by(id=value["category"]).first()).type  for value in current_questions ], 
                    'totals_questions': len(questions)
                })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.(valider)

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/api/category/<string:category>/questions' , methods=['GET'])
    def search_questions_by_category(category):
        question=Question.query.filter_by(category = category).all()
        current_questions = paginate_plants(request, question)
        if len(current_questions) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'current_category':[ (Category.query.filter_by(id=value["category"]).first()).type  for value in current_questions ],
                'totals_questions': len(Question.query.filter_by(category = category).all())
            })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.(valider)

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/api/quizzes' , methods=['POST'])
    def play_quiz():
        body = request.get_json() 
        if "quiz_category" not in body or  "previous_questions" not in body : 
            abort(404)
        if  body.get('quiz_category')["id"] == 0 :
            question=Question.query.all()
            if len(question) == 0 :
                abort(404)
            else:
                random_choice = random.choice([ value for value in question if value.id not in body.get('previous_questions')])
                return jsonify({
                    'success': True,
                    'question': random_choice.format(),
                    'totals_questions': len(Question.query.all())
                })
        else:
            question=Question.query.filter(Question.category == body.get('quiz_category')["id"] ).all()
            if len(question) == 0 :
                abort(404)
            else:
                random_choice = random.choice(question)
                if random_choice.id not in body.get('previous_questions'):
                    return jsonify({
                        'success': True,
                        'question': random_choice.format(),
                        'totals_questions': len(Question.query.filter(Question.category == body.get('quiz_category')["id"] ).all())
                    })
                else:
                    return jsonify({
                        'success': True,
                        'question': False ,
                        'totals_questions': 0
                    })


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({'success': False, 'error': 404,
                'message': 'Not found'}), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({'success': False, 'error': 422,
                'message': 'unprocessable'}), 422)

    @app.errorhandler(400)
    def error_client(error):
        return (jsonify({'success': False, 'error': 400,
                'message': 'Bad request'}), 400)

    @app.errorhandler(500)
    def server_error(error):
        return (jsonify({'success': False, 'error': 500,
                'message': 'internal server error'}), 500)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (jsonify({'success': False, 'error': 405,
                'message': 'method not allowed'}), 405)


    @app.errorhandler(401)
    def unauthorized(error):
        return (jsonify({'success': False, 'error': 401,
                'message': 'unauthorized'}), 401)

    return app

