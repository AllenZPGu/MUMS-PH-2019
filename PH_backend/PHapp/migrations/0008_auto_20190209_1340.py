# Generated by Django 2.1.5 on 2019-02-09 02:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PHapp', '0007_auto_20190209_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedguesses',
            name='team',
            field=models.ForeignKey(db_column='team', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
