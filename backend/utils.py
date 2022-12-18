"""Project Utils."""

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    """Formats date based on the supplied input.
        Args:
            request (str): The request
            selection (str): current selection
        Returns:
            str: The formatted date
        """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions
