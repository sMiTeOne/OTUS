from django.urls import path

from . import views

urlpatterns = [
    path("", views.SearchQuestion.as_view(), name="search"),
    path("tag/<str:tag>", views.SearchQuestionTag.as_view(), name="search_tag"),
]
