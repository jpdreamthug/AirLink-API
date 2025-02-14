# Generated by Django 5.0.8 on 2024-08-07 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airlink_api", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airplane",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="airplane",
            name="rows",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="airplane",
            name="seats_in_row",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="airport",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AddConstraint(
            model_name="route",
            constraint=models.UniqueConstraint(
                fields=("source", "destination"), name="unique_route"
            ),
        ),
    ]
