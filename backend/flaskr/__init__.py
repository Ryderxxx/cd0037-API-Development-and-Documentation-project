import os
import sys
import random
from crypt import methods
from unicodedata import category

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import Category, Question, setup_db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    """
    @TODO: Done
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #CORS(app, resources={'/':{'origins':'*'}})
    CORS(app, origins='*')


    """
    @TODO: Done
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,DELETE"
        )
        return response


    """
    @TODO: Done
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def retrieve_categories():
        categories_dict = {}
        categories = Category.query.all()
        if len(categories) == 0:
            return abort(404)
        for category in categories:
            categories_dict[category.id] = category.type
        return jsonify({
            'success': True, 
            'categories': categories_dict
            }), 200


    """
    @TODO: Done
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        categories_dict = {}
        questions = Question.query.paginate(per_page=QUESTIONS_PER_PAGE).items
        categories = Category.query.all()
        if len(questions)*len(categories) == 0:
            return abort(404)
        questions_list = [question.format() for question in questions]
        for category in categories:
            categories_dict[category.id] = category.type
        return jsonify({
            'success': True,
            'questions': questions_list,
            'totalQuestions': Question.query.count(),
            'categories': categories_dict,
            'currentCategory': None
        }), 200
        

    """
    @TODO: Done
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question_by_id(id):
        try:
            Question.query.get(id).delete()
            return jsonify({
                'success': True, 
                'id': id
            }), 200
        except:
            return abort(422)


    """
    @TODO: Done
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    """
    @TODO: Done
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    @app.route('/questions', methods=['POST'])
    def search_or_create_questions():
        search_term = request.get_json().get('searchTerm')
        if search_term:
            search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results], 
                'total_questions': len(search_results)
            })
        else:
            try:
                answer = request.get_json().get('answer')
                question = request.get_json().get('question')
                category = request.get_json().get('category')
                difficulty = request.get_json().get('difficulty')
                if all(variable is not None for variable in [answer, question, category, difficulty]):
                    Question(answer=answer, question=question, category=category, difficulty=difficulty).insert()
                    return jsonify({'success': True}), 200
            except:
                return abort(422)
            return abort(400)
            

    """
    @TODO: Done
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        category = Category.query.get(category_id)
        if category is None:
            return abort(404)
        questions_list = [question.format() for question in Question.query.filter_by(category=category_id).all()]
        return jsonify({
            'success': True,
            'questions': questions_list,
            'totalQuestions': len(questions_list),
            'currentCategory': category.type
        }), 200

    """
    @TODO: Done
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def retrieve_quiz_question():
        quiz_category = request.get_json().get('quiz_category')
        previous_questions = request.get_json().get('previous_questions')
        if quiz_category is None or previous_questions is None or not quiz_category.__contains__('id'):
            return abort(400)
        if quiz_category['id'] == 0:
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter(Question.category==quiz_category['id'], Question.id.notin_(previous_questions)).all()
        if questions:
            return jsonify({
                'success': True,
                'question': random.choice(questions).format()
            }), 200
        return jsonify({'success': True}), 200
        

    """
    @TODO: Done
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400,
                     "message": "bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404,
                    "message": "resource not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({"success": False, "error": 422,
                    "message": "unprocessable"}), 422
        
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"success": False, "error": 500,
                     "message": "internal server error"}), 500

    return app

