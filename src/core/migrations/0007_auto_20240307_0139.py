# Generated by Django 3.2.25 on 2024-03-07 01:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_alter_round_submission"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="disabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="game",
            name="slug",
            field=models.SlugField(
                help_text="Used in the url for your game.",
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
