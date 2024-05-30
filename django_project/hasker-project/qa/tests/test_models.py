from qa.models import (
    Tag,
    Vote,
    Answer,
    Question,
)
from django.test import TestCase
from account.models import User


class TestHordeVoting(TestCase):
    """
    test upvotes and downvotes
    """

    expected_rating = 10

    @classmethod
    def setUpTestData(cls):
        users = []
        for i in range(cls.expected_rating):
            user = User.objects.create_user(username="user-{:03d}".format(i), password="123456")
            user.save()
            users.append(user)

        q = Question.objects.create(author=users[0], slug="qwerty")
        a = Answer.objects.create(author=users[1], question=q)

        for user in users:
            q.update_rating(user, 1)
            a.update_rating(user, -1)

    def setUp(self):
        pass

    def test_rating(self):
        q = Question.objects.first()
        a = Answer.objects.first()
        votes_count = Vote.objects.count()
        self.assertEqual(q.rating, self.expected_rating)
        self.assertEqual(a.rating, -self.expected_rating)
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
        q = Question.objects.create(author=self.user, slug="qwe")
        Answer.objects.create(author=self.user, question=q)

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
        """
        check if vote reset when user votes twice on the same item

        :return:
        """
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
        q = Question.objects.create(author=self.user, slug="qwe")
        Answer.objects.create(author=self.user, question=q)
        Answer.objects.create(author=self.user, question=q)

    def test_answers(self):
        q = Question.objects.first()
        answers = Answer.objects.filter(question=q)
        self.assertEqual(len(answers), 2)
        # approve first answer
        answers[0].approve()
        q.refresh_from_db()
        for answer in answers:
            answer.refresh_from_db()
        self.assertEqual(q.approved_answer, answers[0])
        self.assertTrue(answers[0].approved)
        self.assertFalse(answers[1].approved)

        # approve the second answer, expect first answer will be "disapproved"
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
        cls.q = Question.objects.create(title="question", content="question")
        cls.tags = {"tag_{:02}".format(i) for i in range(5)}

        for tag in cls.tags:
            t = Tag.objects.create(title=tag)
            cls.q.tags.add(t)

    def test_tags_list(self):
        tags = set(self.q.tags_list)
        self.assertEqual(tags, self.__class__.tags)
