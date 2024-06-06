from qa.models import (
    Tag,
    Question,
)
from django.test import TestCase
from django.urls import reverse


class TestSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        tag1 = Tag(title="python")
        tag2 = Tag(title="django")

        tag1.save()
        tag2.save()

        question1 = Question(title="Python", content="django")
        question2 = Question(title="Django", content="python")

        question1.save()
        question2.save()

        question1.tags.add(tag1)
        question2.tags.add(tag2)

    def test_query_search(self):
        response = self.client.get(reverse("search"), {"q": "python"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questions"]), 2)

    def test_tag_query_search(self):
        response = self.client.get(reverse("search"), {"q": "tag:django"})
        self.assertEqual(response.status_code, 302)

    def test_tag_search(self):
        cases = (
            ("python", 1),
            ("django", 1),
            ("flask", 0),
        )

        for tag, expected in cases:
            with self.subTest(tag=tag, expected=expected):
                response = self.client.get(reverse("search_tag", kwargs={"tag": tag}))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context["questions"]), expected)
