# Generated by Django 2.1.7 on 2019-02-24 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PHapp', '0024_teams_guesses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correctguesses',
            name='puzzle',
        ),
        migrations.RemoveField(
            model_name='correctguesses',
            name='subGuessKey',
        ),
        migrations.RemoveField(
            model_name='correctguesses',
            name='team',
        ),
        migrations.DeleteModel(
            name='CorrectGuesses',
        ),
    ]