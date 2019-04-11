# Generated by Django 2.2 on 2019-04-11 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("api", "0064_improve_site_profile")]

    operations = [
        migrations.AddField(
            model_name="allowedlist",
            name="org_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", ""),
                    ("Production", "Production"),
                    ("Scratch", "Scratch"),
                    ("Sandbox", "Sandbox"),
                    ("Developer", "Developer"),
                ],
                max_length=64,
            ),
        )
    ]
