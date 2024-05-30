from qa.models import Question
from django.shortcuts import redirect
from django.views.generic import ListView
from django.db.models.query import QuerySet


class BaseQuestionSearch(ListView):
    model = Question
    paginate_by = 20
    context_object_name = 'questions'
    ordering = ("-rating", "created_at")


class SearchQuestion(BaseQuestionSearch):
    template_name = "search/results.html"

    def get(self, *args, **kwargs):
        q = self.request.GET.get("q", "")
        if q.startswith("tag:"):
            return redirect("search_tag", q[4:])
        else:
            return super(SearchQuestion, self).get(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        q = self.request.GET.get("q", "")
        return Question.search(q).order_by(*self.ordering)


class SearchQuestionTag(BaseQuestionSearch):
    template_name = "search/tag_results.html"

    def get_queryset(self) -> QuerySet:
        tag = self.kwargs['tag']
        return Question.questions.filter(tags__title__icontains=tag).order_by(*self.ordering)
