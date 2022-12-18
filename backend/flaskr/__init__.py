import random
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, Question, Category
from utils import paginate_questions


def create_app(test_config=None):
    """The trivia app api"""

    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        """ Handle after_request response"""

        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS"
        )

        return response

    @app.route("/categories", methods=["GET"])
    def fetch_categories():
        """ Get categories """

        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        category_list = {category.id: category.type for category in categories}
        return jsonify(
            {
                "success": True,
                "categories": category_list,
                "total_categories": len(categories),
            }
        )

    @app.route("/questions", methods=["GET"])
    def fetch_questions():
        """ Get questions """

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()

        category_list = {category.id: category.type for category in categories}
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "categories": category_list,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """ Delete questions """

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except BaseException:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_question():
        """ Create a question """

        body = request.get_json()

        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        new_question = body.get("question", None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except BaseException:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        """ Get questions by search term """

        body = request.get_json()

        search_term = body.get("searchTerm", None)

        try:
            if search_term:

                selection = Question.query.filter(
                    Question.question.ilike(
                        '%' + search_term + '%')).all()

                current_questions = paginate_questions(request, selection)

                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(current_questions),
                })
            else:
                abort(404)
        except BaseException:
            abort(422)

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def fetch_questions_by_category(category_id):
        """ Get questions by category """

        selection = Question.query.filter(
            Question.category == str(category_id)
        )
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection.all()),
                "current_category": category_id
            }
        )

    @app.route("/quizzes", methods=["POST"])
    def fetch_quizzes():
        """ Get quizzes by category and previous questions """

        try:
            body = request.get_json()
            previous_questions = body.get("previous_questions", None)
            category = body.get("quiz_category", None)
            category_id = category["id"]

            if category_id == 0:
                quiz_list = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                quiz_list = Question.query.filter(
                    Question.category == str(category_id)
                ).filter(
                    Question.id.notin_(previous_questions)
                ).all()

            if len(quiz_list) > 0:
                new_question = quiz_list[random.randrange(
                    0, len(quiz_list))].format()
            else:
                new_question = None

            return jsonify({
                "success": True,
                "question": new_question
            })

        except BaseException:
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        """ Handle 400 error"""

        return (
            jsonify({
                "success": False,
                "error": 400,
                "message": "bad request"
            }),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        """ Handle 404 error"""

        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
            }),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        """ Handle 422 error"""

        return (
            jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"
            }),
            422,
        )

    @app.errorhandler(500)
    def server_error(error):
        """ Handle 500 error"""

        return (
            jsonify({
                "success": False,
                "error": 500,
                "message": "server error"
            }),
            500,
        )

    return app
