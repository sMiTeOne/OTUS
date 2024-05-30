from .models import Question


def trending_questions(_):
    return {"trending_questions": Question.objects.all().order_by("-rating")[:5]}
