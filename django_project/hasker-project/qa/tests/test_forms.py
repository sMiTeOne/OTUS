from qa.forms import QuestionForm
from django.test import TestCase


class TestForm(TestCase):
    def test_question_form_required_feilds(self):
        requests = [
            ({"title": "not empty"}, "empty content"),
            ({"content": "lorem ipsum"}, "empty title"),
        ]
        for request, msg in requests:
            with self.subTest(request=request, msg=msg):
                form = QuestionForm(request)
                self.assertFalse(form.is_valid())

    def test_question_form_valid(self):
        request = {"title": "Title", "content": "Content"}
        self.assertTrue((QuestionForm(request)).is_valid(), "Question form must be valid")
