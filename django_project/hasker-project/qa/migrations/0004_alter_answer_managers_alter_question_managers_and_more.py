import django.db.models.manager
import django.db.models.deletion
from django.db import (
    models,
    migrations,
)
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("qa", "0003_answer_approved"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="answer",
            managers=[
                ("answers", django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name="question",
            managers=[
                ("questions", django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name="answer",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="answers",
                to="qa.question",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="questions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
