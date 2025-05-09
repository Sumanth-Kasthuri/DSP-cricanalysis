# Generated by Django 5.1.6 on 2025-05-01 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0002_favoriteteam"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="favoriteteam",
            options={
                "verbose_name": "Favorite Team",
                "verbose_name_plural": "Favorite Teams",
            },
        ),
        migrations.RenameField(
            model_name="favoriteteam",
            old_name="date_added",
            new_name="added_on",
        ),
        migrations.RenameField(
            model_name="favoriteteam",
            old_name="team_short_name",
            new_name="team_sname",
        ),
        migrations.AlterField(
            model_name="favoriteteam",
            name="team_id",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="favoriteteam",
            name="team_name",
            field=models.CharField(max_length=100),
        ),
    ]
