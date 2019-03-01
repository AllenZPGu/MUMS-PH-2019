# Generated by Django 2.1.7 on 2019-02-20 05:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PHapp', '0019_auto_20190220_1607'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorrectGuesses',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('submitTime', models.DateTimeField(null=True)),
                ('puzzle', models.ForeignKey(db_column='puzzle', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='PHapp.Puzzles')),
                ('subGuessKey', models.ForeignKey(db_column='subGuessKey', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='PHapp.SubmittedGuesses')),
                ('team', models.ForeignKey(db_column='team', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='PHapp.Teams')),
            ],
            options={
                'db_table': 'CorrectGuesses',
            },
        ),
    ]