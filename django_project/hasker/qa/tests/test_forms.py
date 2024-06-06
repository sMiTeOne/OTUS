from qa.forms import QuestionForm
from django.test import TestCase


class TestForm(TestCase):
    FIELDS = ('title', 'content')

    def test_question_form_required_fields(self):
        for field_name in self.FIELDS:
            request = {field_name: field_name}
            with self.subTest(request=request):
                form = QuestionForm(request)
                self.assertFalse(form.is_valid())

    def test_question_form_valid(self):
        request = {"title": "title", "content": "content"}
        self.assertTrue((QuestionForm(request)).is_valid())
