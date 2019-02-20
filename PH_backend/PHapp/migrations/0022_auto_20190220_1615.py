# Generated by Django 2.1.7 on 2019-02-20 05:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PHapp', '0021_remove_correctguesses_submittime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='correctguesses',
            name='team',
            field=models.ForeignKey(db_column='team', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='submittedguesses',
            name='team',
            field=models.ForeignKey(db_column='team', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
