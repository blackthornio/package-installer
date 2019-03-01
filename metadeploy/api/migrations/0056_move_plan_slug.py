# Generated by Django 2.1.7 on 2019-02-28 19:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("api", "0055_no_null_plan_template")]

    operations = [
        migrations.AlterField(
            model_name="planslug",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="api.PlanTemplate"
            ),
        )
    ]
