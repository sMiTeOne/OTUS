from collections.abc import Sequence

from qa.forms import (
    AnswerForm,
    QuestionForm,
)
from django.db import transaction
from django.urls import reverse_lazy
from hasker.utils import wrap_with_paginator
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.views.generic import (
    FormView,
    ListView,
    CreateView,
    UpdateView,
)
from django.db.models.query import QuerySet
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import (
    Answer,
    Question,
)


class ShowQuestions(ListView):
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = "qa/main.html"

    def get_queryset(self) -> QuerySet:
        ordering = self.get_ordering()
        return Question.questions.order_by(ordering)

    def get_ordering(self) -> str:
        ordering = self.request.GET.get("sort", "id")
        return f"-{ordering}"


class CreateQuestion(CreateView):
    form_class = QuestionForm
    success_url = reverse_lazy("index")
    template_name = "qa/create_question.html"


def show_question(request, slug):
    q = get_object_or_404(Question.questions, slug=slug)
    page = request.GET.get("page", 1)
    answers_list = Answer.answers.filter(question=q).order_by("-rating", "created_at")
    answers = wrap_with_paginator(
        objects_list=answers_list,
        page=page,
        per_page=30,
    )
    return render(
        request,
        "qa/show_question.html",
        {"question": q, "form": AnswerForm(), "answers": answers},
    )


# class CreateAnswer(CreateView):
#     form_class = AnswerForm
#     success_url = reverse_lazy("show_question")
#     template_name = "qa/show_question.html"


@login_required(login_url=reverse_lazy("login"))
@require_POST
def create_answer(request, slug):
    form = AnswerForm(request.POST)
    if form.is_valid():
        a = form.save(commit=False)  # type: Answer
        a.bind_with_question_and_user(slug, request.user)
        a.send_notification(request)
    return redirect("show_question", slug)


@login_required(login_url=reverse_lazy("login"))
@require_POST
def vote_answer(request, slug, pk, value):
    a = get_object_or_404(Answer, pk=pk)
    a.update_rating(request.user, int(value))
    return redirect("show_question", slug)


@login_required(login_url=reverse_lazy("login"))
@require_POST
def vote_question(request, slug, value):
    q = get_object_or_404(Question, slug=slug)
    q.update_rating(request.user, int(value))
    return redirect("show_question", slug)


@login_required(login_url=reverse_lazy("login"))
@require_POST
def approve_answer(request, slug, pk):
    a = get_object_or_404(Answer, pk=pk)
    a.approve()
    return redirect("show_question", slug)
