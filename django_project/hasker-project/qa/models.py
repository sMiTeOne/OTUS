import itertools
from enum import IntEnum

from django.db import (
    models,
    transaction,
)
from unidecode import unidecode
from django.http import HttpRequest
from django.urls import reverse
from account.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.template.loader import render_to_string
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)

from .managers import (
    AnswerManager,
    QuestionManager,
    ApiQuestionManager,
)


class BaseQAItems(IntEnum):
    QUESTION = 1
    ANSWER = 2


class Tag(models.Model):
    title = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.title


class Vote(models.Model):
    value = models.IntegerField()
    item_id = models.IntegerField()
    item_type = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("user", "item_id", "item_type"),)


class BaseQAItem(models.Model):
    item_type = None
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    rating = models.IntegerField(default=0)
    objects = models.Manager()

    @transaction.atomic
    def update_rating(self, user: User, value: int):
        vote = Vote.objects.filter(item_type=self.item_type, item_id=self.id, user=user.id)
        if vote.exists():
            self.rating -= vote[0].value
            vote.delete()
        else:
            Vote.objects.create(user=user, item_type=self.item_type, item_id=self.id, value=value)
            self.rating += value
        self.save()

    class Meta:
        abstract = True


class Question(BaseQAItem):
    item_type = BaseQAItems.QUESTION
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    tags = models.ManyToManyField(Tag, blank=True)
    approved_answer = models.ForeignKey("Answer", null=True, on_delete=models.SET_NULL, related_name="approved_answer")

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="questions")
    questions = QuestionManager()

    def __str__(self):
        return self.title

    def save(self):
        if not self.slug:
            self.slug = self._unique_slug(self.title)
        super().save()

    def save_author_and_tags(self, request: HttpRequest):
        self.author = request.user
        self.save()
        for tag_id in request.POST.getlist("tags", []):
            self.tags.add(tag_id)

    @staticmethod
    def _unique_slug(value):
        slug = slugify(unidecode(value))
        unique_slug = slug
        for i in itertools.count():
            if Question.objects.filter(slug=unique_slug).exists():
                unique_slug = "{}-{}".format(slug, i)
            else:
                return unique_slug

    @staticmethod
    def search(q):
        search_vector = SearchVector("content") + SearchVector("title")
        search_query = None
        for token in q.split():
            token = token.strip()
            if search_query:
                search_query &= SearchQuery(token)
            else:
                search_query = SearchQuery(token)

        return Question.questions.annotate(search=search_vector).filter(search=search_query)

    @property
    def tags_list(self):
        return self.tags.values_list("title", flat=True)


class Answer(BaseQAItem):
    item_type = BaseQAItems.ANSWER
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    approved = models.BooleanField(default=False)
    answers = AnswerManager()

    @transaction.atomic
    def approve(self):
        current_answer = self.question.approved_answer

        if current_answer:
            current_answer.approved = False
            current_answer.save()

        if current_answer == self:
            self.question.approved_answer = None
        else:
            self.question.approved_answer = self
            self.approved = True
            self.save()
        self.question.save()

    @transaction.atomic
    def set_question_and_user(self, slug: str, user: User):
        self.question = get_object_or_404(Question, slug=slug)
        self.author = user
        self.save()

    def send_notification(self, request: HttpRequest):
        ctx = {
            "answer": self,
            "link": request.build_absolute_uri(reverse("show_question", kwargs={"slug": self.question.slug})),
        }
        plain_message = render_to_string("emails/new_answer.txt", ctx)
        html_message = render_to_string("emails/new_answer.html", ctx)
        send_mail(
            subject="New answer on Hasker",
            message=plain_message,
            from_email="noreply@hasker.com",
            recipient_list=[self.question.author.email],
            html_message=html_message,
            fail_silently=False,
        )
