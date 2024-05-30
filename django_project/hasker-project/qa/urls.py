from django.urls import (
    path,
    include,
)

from . import views

urlpatterns = [
    path("create/", views.CreateQuestion.as_view(), name="create_question"),
    # path("create/", views.create_question, name="create_question"),
    path("question/<str:slug>/", views.show_question, name="show_question"),
    path(
        "question/<str:slug>/vote/<str:value>",
        views.vote_question,
        name="vote_question",
    ),
    path(
        "question/<str:slug>/answer/",
        include(
            [
                path("", views.create_answer, name="create_answer"),
                # path("", views.CreateAnswer.as_view(), name="create_answer"),
                path("<int:pk>/vote/<str:value>/", views.vote_answer, name="vote_answer"),
                path("<int:pk>/approve/", views.approve_answer, name="approve_answer"),
            ]
        ),
    ),
]
