from qa.models import Question
from django.test import TestCase
from django.urls import reverse
from account.models import User


class TestPagination(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="test1", email="test1@hasker.com", password="123456")
        for i in range(100):
            Question.objects.create(
                title="Question {}".format(i),
                slug="question_{}".format(i),
                content="lorem ipsum blah blah",
                author=user,
            )

    def test_questions_pagination(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context["questions"]),
            20,
        )
