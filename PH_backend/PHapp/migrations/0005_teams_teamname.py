# Generated by Django 2.1.5 on 2019-02-09 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PHapp', '0004_auto_20190209_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='teams',
            name='teamName',
            field=models.CharField(max_length=50, null=True),
        ),
    ]