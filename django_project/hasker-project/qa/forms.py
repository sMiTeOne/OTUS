from django.forms import (
    ModelForm,
    CharField,
)

from .models import (
    Answer,
    Question,
)


class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ("title", "content", "tags")


class AnswerForm(ModelForm):
    content = CharField(label="Answer")

    class Meta:
        model = Answer
        fields = ("content",)
