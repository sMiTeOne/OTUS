from django.db import (
    models,
    migrations,
)


class Migration(migrations.Migration):
    dependencies = [
        ("qa", "0002_auto_20190103_1613"),
    ]

    operations = [
        migrations.AddField(
            model_name="answer",
            name="approved",
            field=models.BooleanField(default=False),
        ),
    ]
