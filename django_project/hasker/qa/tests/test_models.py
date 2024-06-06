from qa.models import (
    Tag,
    Vote,
    Answer,
    Question,
)
from django.test import TestCase
from account.models import User


class TestHordeVoting(TestCase):
    expected_rating = 10

    @classmethod
    def setUpTestData(cls):
        users = []
        for i in range(cls.expected_rating):
            user = User.objects.create_user(username="user-{:03d}".format(i), password="123456")
            user.save()
            users.append(user)

        question = Question(author=users[0], slug="qwerty")
        answer = Answer(author=users[1], question=question)
        question.save()
        answer.save()

        for user in users:
            question.update_rating(user, 1)
            answer.update_rating(user, -1)

    def test_rating(self):
        question = Question.objects.first()
        answer = Answer.objects.first()
        votes_count = Vote.objects.count()
        self.assertEqual(question.rating, self.expected_rating)
        self.assertEqual(answer.rating, -self.expected_rating)
        self.assertEqual(votes_count, 2 * self.expected_rating)


class TestSinglePersonVoting(TestCase):
    expected_rating = 0
    user = None

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username="username", password="123456")
        user.save()
        cls.user = user

    def setUp(self):
        Question.objects.all().delete()
        Answer.objects.all().delete()
        question = Question(author=self.user, slug="qwerty")
        answer = Answer(author=self.user, question=question)
        question.save()
        answer.save()

    def test_vote_once(self):
        q = Question.objects.first()
        a = Answer.objects.first()
        q.update_rating(self.user, 1)
        a.update_rating(self.user, 1)
        votes_count = Vote.objects.count()
        self.assertEqual(q.rating, 1)
        self.assertEqual(a.rating, 1)
        self.assertEqual(votes_count, 2)

    def test_vote_twice(self):
        q = Question.objects.first()
        a = Answer.objects.first()
        q.update_rating(self.user, 1)
        a.update_rating(self.user, 1)
        q.update_rating(self.user, 1)
        a.update_rating(self.user, 1)
        votes_count = Vote.objects.count()
        self.assertEqual(q.rating, 0)
        self.assertEqual(a.rating, 0)
        self.assertEqual(votes_count, 0)


class TestAnswerApprove(TestCase):
    user = None

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username="username", password="123456")
        user.save()
        cls.user = user

    def setUp(self):
        Question.objects.all().delete()
        Answer.objects.all().delete()
        question = Question(author=self.user, slug="qwe")
        question.save()
        Answer(author=self.user, question=question).save()
        Answer(author=self.user, question=question).save()

    def test_answers(self):
        q = Question.objects.first()
        answers = Answer.objects.filter(question=q)
        self.assertEqual(len(answers), 2)
        answers[0].approve()
        q.refresh_from_db()
        for answer in answers:
            answer.refresh_from_db()
        self.assertEqual(q.approved_answer, answers[0])
        self.assertTrue(answers[0].approved)
        self.assertFalse(answers[1].approved)

        answers[1].approve()
        q.refresh_from_db()
        for answer in answers:
            answer.refresh_from_db()
        self.assertEqual(q.approved_answer, answers[1])
        self.assertTrue(answers[1].approved)
        self.assertFalse(answers[0].approved)


class TestTagsList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question(title="question", content="question")
        cls.question.save()
        cls.tags = {f"tag_{i}" for i in range(5)}

        for tag in cls.tags:
            tag = Tag(title=tag)
            tag.save()
            cls.question.tags.add(tag)

    def test_tags_list(self):
        tags = set(self.question.tags_list)
        self.assertEqual(tags, self.__class__.tags)
