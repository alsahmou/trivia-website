import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug.exceptions import HTTPException

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Returns a dictionary of {id:type} for all categories


def get_categories_dict(categories):
  categories_dict = {}
  for category in categories:
    categories_dict[category.id] = category.type.lower()
  return(categories_dict)


def paginate_questions(request, questions):
  current_questions = []
  page = request.args.get('page', 1, type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in questions]
  current_questions = questions[start:end]
  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  CORS(app, resources={r"/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    if(len(categories) == 0):
      abort(404)
    return jsonify({
      'success': True,
      'categories': get_categories_dict(categories)
    })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)
    if(len(current_questions) == 0):
      abort(404)
    categories = Category.query.order_by(Category.id).all()
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': get_categories_dict(categories),
    })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      else:
        question.delete()
        return get_questions()
      
    except:
      abort(422)

  
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      return get_questions()

    except:
      abort(422)
      

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    current_questions = paginate_questions(request, questions)
    if(len(current_questions) == 0):
      abort(404)
    categories = Category.query.order_by(Category.id).all()
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': get_categories_dict(categories),
    })


  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
      abort(404)

    questions = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
    current_questions = paginate_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'current_category': category_id
    })


  '''
@TODO:
Create a POST endpoint to get questions to play the quiz.
This endpoint should take category and previous question parameters
and return a random questions within the given category,
if provided, and that is not one of the previous questions.

TEST: In the "Play" tab, after a user selects "All" or a category,
one question at a time is displayed, the user is allowed to answer
and shown whether they were correct or not.
'''
  @app.errorhandler(HTTPException)
  def handle_exception(e):
    return jsonify({
      "success": False,
      "error": e.code,
      "message": e.name
    }), e.code

  '''
@TODO:
Create error handlers for all expected errors
including 404 and 422.
'''

  return app
