import django.db.models.deletion
from django.db import (
    models,
    migrations,
)


class Migration(migrations.Migration):
    dependencies = [
        ("qa", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="answered",
        ),
        migrations.AddField(
            model_name="question",
            name="approved_answer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="approved_answer",
                to="qa.Answer",
            ),
        ),
    ]
