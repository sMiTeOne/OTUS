from django.db import models


class QuestionManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related("tags")
        queryset = queryset.select_related("author")
        queryset = queryset.prefetch_related("answers")
        return queryset


class ApiQuestionManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("author")
        queryset = queryset.prefetch_related("answers")
        return queryset


class AnswerManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("author")
        return queryset
