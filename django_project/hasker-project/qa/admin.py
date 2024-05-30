from django.contrib import admin

from .models import (
    Tag,
    Answer,
    Question,
)


@admin.register(Question)
class QuestionModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "rating",
        "slug",
        "author",
        "created_at",
    )
    list_filter = ("title",)
    readonly_fields = (
        "rating",
        "created_at",
    )
    fields = (
        "title",
        "slug",
        "content",
        "tags",
        "author",
        "created_at",
        "rating",
    )


@admin.register(Answer)
class AnswerModelAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "rating",
        "author",
        "created_at",
    )
    readonly_fields = (
        "rating",
        "created_at",
    )
    fields = (
        "content",
        "author",
        "created_at",
        "rating",
    )


admin.site.register(Tag)
