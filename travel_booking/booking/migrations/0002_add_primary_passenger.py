from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="primary_passenger_name",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="booking",
            name="primary_passenger_age",
            field=models.PositiveIntegerField(default=18),
        ),
    ]


