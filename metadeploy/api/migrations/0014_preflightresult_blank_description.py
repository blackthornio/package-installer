# Generated by Django 2.1.2 on 2018-10-30 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_preflightresult_status_failed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]