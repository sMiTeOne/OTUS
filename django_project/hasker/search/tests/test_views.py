from qa.models import (
    Tag,
    Question,
)
from django.test import TestCase
from django.urls import reverse


class TestSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        t1 = Tag.objects.create(title="python")
        t2 = Tag.objects.create(title="django")

        Question.objects.create(title="randomize", content="qwerty").tags.add(t1)
        Question.objects.create(title="qwerty", content="random").tags.add(t2)

    def test_if_it_is_searching_in_both_fields(self):
        response = self.client.get(reverse("search"), {"q": "randomization other"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questions"]), 2)

    def test_search_tag(self):
        cases = [
            ("python", 1),
            ("django", 1),
            ("rails", 0),
        ]

        for tag, expected in cases:
            with self.subTest(tag=tag, expected=expected):
                response = self.client.get(reverse("search_tag", kwargs={"tag": tag}))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context["questions"]), expected)