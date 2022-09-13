import json
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.debug = True
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/api/categories")
    def categories():
        results = Category.query.all()
        categories = {}
        for category in results:
            categories.update({category.id: category.type})

        return jsonify({"categories": categories})
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.


    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/api/questions")
    def get_questions():
        page = request.args.get('page', 1, type=int)
        results = Question.query.paginate(
            page, QUESTIONS_PER_PAGE, False)
        questions = []
        categories = {}
        categories_results = Category.query.all()
        for category in categories_results:
            categories.update({category.id: category.type})
        for result in results.items:
            if result:
                questions.append({
                    "id": result.id,
                    "question": result.question,
                    "answer": result.answer,
                    "difficulty": result.difficulty,
                    "category": result.category
                })
        return jsonify({
            "questions": questions,
            "totalQuestions": results.total,
            "categories": categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/api/questions/<question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = None
        try:
            question = Question.query.get(question_id)
            if question == None:
                return jsonify({"success": False}), 404
            db.session.delete(question)
            db.session.commit()
        except:
            return jsonify({"success": False}), 500

        return jsonify({"success": True})

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/api/questions", methods=["POST"])
    def create_question():
        data = request.get_json()
        if not "answer" in data or not "question" in data:
            return jsonify({"success": False}), 401
        question = Question(
            question=data["question"],
            answer=data["answer"],
            difficulty=data["difficulty"],
            category=data["category"]
        )
        db.session.add(question)
        db.session.commit()
        db.session.close()
        return jsonify({"success": True})

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/api/questions/search", methods=["POST"])
    def search_question():
        if not 'searchTerm' in request.get_json():
            return jsonify({"success": False}), 401
        results = Question.query.filter(Question.question.ilike(r"%{}%".format(
            request.get_json()['searchTerm']))).all()
        questions = []

        for result in results:
            questions.append({
                "id": result.id,
                "question": result.question,
                "answer": result.answer,
                "difficulty": result.difficulty,
                "category": result.category
            })

        return jsonify({"questions": questions, "totalQuestions": len(results)})

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/api/quizzes", methods=["POST"])
    def get_next_question():
        data = request.get_json()
        if not "quiz_category" in data:
            return jsonify({"success": False}), 401
        questions = []
        selectedQuestion = None
        previousQuestions = data['previous_questions']
        quizCategory = data['quiz_category']

        if int(quizCategory["id"]) == 0:
            questions = Question.query.all()
        else:
            questions = db.session.query(
                Question).filter_by(category=str(quizCategory["id"])).all()

        while True:
            question = random.choice(questions)
            questionFound = False
            for previousQuestion in previousQuestions:
                if int(question.id) == int(previousQuestion):
                    questionFound = True
            if not questionFound:
                selectedQuestion = question
                break

        return jsonify({
            "question": {
                "id": selectedQuestion.id,
                "question": selectedQuestion.question,
                "answer": selectedQuestion.question,
                "difficulty": selectedQuestion.difficulty,
                "category": selectedQuestion.category
            }
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/api/categories/<category_id>/questions")
    def get_questions_by_category(category_id):
        currentCategory = Category.query.get(category_id)
        if not currentCategory:
            return jsonify({"success": False}), 401
        results = Question.query.filter_by(category=category_id).all()
        questions = []
        for result in results:
            questions.append({
                "id": result.id,
                "question": result.question,
                "answer": result.answer,
                "difficulty": result.difficulty,
                "category": result.category
            })
        return jsonify({
            "questions": questions,
            "totalQuestions": len(results),
            "currentCategory": currentCategory.type
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def error_404(e):
        return "Invalid route."

    @app.errorhandler(400)
    def error_400(e):
        return "Bad request"

    @app.errorhandler(422)
    def error_422(e):
        return "Unable to process the request"

    @app.errorhandler(500)
    def ierror_500(e):
        return "An internal error occured"

    return app
