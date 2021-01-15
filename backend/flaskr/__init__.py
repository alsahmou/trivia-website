import os
from flask import Flask, request, abort, jsonify, json
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

def get_question_dict(question):
  if question is None:
    return
  question_dict = {}
  question_dict['question'] = question.question
  question_dict['answer'] = question.answer
  question_dict['id'] = question.id
  return question_dict

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

  
  @app.route('/questions/submit', methods=['POST'])
  def submit_question():
    body = request.get_json()

    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')

    if not new_question or not new_answer or not new_category or not new_difficulty:
      abort(422)

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

  
  @app.route('/quizzes/play', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    try:
      previous_questions = body.get('previous_questions')
      quiz_category = body.get('quiz_category')['id']

      if previous_questions is None or quiz_category is None:
        abort(400)
      
      if quiz_category == 0:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions),Question.category == quiz_category).all()
      current_question = None
      if len(questions) > 0:
        current_question = random.choice(questions)
      

      return jsonify({
        'success': True,
        'question': get_question_dict(current_question)
      })

    except:
      abort(400)

  

  @app.errorhandler(HTTPException)
  def handle_exception(e):
    return jsonify({
      "success": False,
      "error": e.code,
      "message": e.name
    }), e.code



  return app
