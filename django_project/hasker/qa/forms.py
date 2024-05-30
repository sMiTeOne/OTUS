from django.forms import (
    Textarea,
    CharField,
    ModelForm,
)

from .models import (
    Answer,
    Question,
)


class QuestionForm(ModelForm):
    title = CharField(label="Заголовок")
    content = CharField(label="Описание", widget=Textarea)

    class Meta:
        model = Question
        fields = ("title", "content", "tags")


class AnswerForm(ModelForm):
    content = CharField(label="Ответ", widget=Textarea)

    class Meta:
        model = Answer
        fields = ("content",)
