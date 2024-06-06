from qa.forms import (
    AnswerForm,
    QuestionForm,
)
from django.urls import reverse_lazy
from django.shortcuts import (
    redirect,
    get_object_or_404,
)
from django.views.generic import (
    ListView,
    CreateView,
)
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import (
    Answer,
    Question,
)


class ShowQuestions(ListView):
    model = Question
    paginate_by = 20
    context_object_name = "questions"
    template_name = "qa/main.html"

    def get_ordering(self) -> str:
        ordering = self.request.GET.get("sort", "id")
        return f"-{ordering}"


class ShowAnswers(ListView):
    model = Answer
    template_name = "qa/show_question.html"
    context_object_name = "answers"
    ordering = ("-rating", "created_at")
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = self.get_question()
        context["form"] = AnswerForm()
        return context

    def get_question(self) -> Question | None:
        return get_object_or_404(Question, slug=self.kwargs['slug'])


class CreateQuestion(CreateView):
    form_class = QuestionForm
    success_url = reverse_lazy("index")
    template_name = "qa/create_question.html"


@login_required(login_url=reverse_lazy("login"))
@require_POST
def create_answer(request, slug):
    form = AnswerForm(request.POST)
    if form.is_valid():
        a: Answer = form.save(commit=False)
        a.set_question_and_user(slug, request.user)
        a.send_notification(request)
    return redirect("show_question", slug)


@login_required(login_url=reverse_lazy("login"))
@require_POST
def vote_answer(request, slug, pk, value):
    answer = get_object_or_404(Answer, pk=pk)
    answer.update_rating(request.user, int(value))
    return redirect("show_question", slug)


@login_required(login_url=reverse_lazy("login"))
@require_POST
def vote_question(request, slug, value):
    question = get_object_or_404(Question, slug=slug)
    question.update_rating(request.user, int(value))
    return redirect("show_question", slug)


@login_required(login_url=reverse_lazy("login"))
@require_POST
def approve_answer(request, slug, pk):
    answer = get_object_or_404(Answer, pk=pk)
    answer.approve()
    return redirect("show_question", slug)
