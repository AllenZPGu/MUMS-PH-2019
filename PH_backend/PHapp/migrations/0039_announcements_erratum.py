# Generated by Django 2.0.2 on 2019-08-11 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PHapp', '0038_auto_20190809_0032'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcements',
            name='erratum',
            field=models.BooleanField(default=False),
        ),
    ]
