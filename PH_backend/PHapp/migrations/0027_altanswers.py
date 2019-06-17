# Generated by Django 2.1.7 on 2019-05-06 03:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PHapp', '0026_auto_20190302_0004'),
    ]

    operations = [
        migrations.CreateModel(
            name='AltAnswers',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('altAnswer', models.CharField(max_length=500, null=True)),
                ('puzzle', models.ForeignKey(db_column='puzzle', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='PHapp.Puzzles')),
            ],
            options={
                'db_table': 'AltAnswers',
            },
        ),
    ]