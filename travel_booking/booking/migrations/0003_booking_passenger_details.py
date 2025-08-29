from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0002_add_primary_passenger"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="passenger_details",
            field=models.JSONField(default=list),
        ),
    ]


