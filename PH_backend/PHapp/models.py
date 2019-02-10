from django.db import models
from django.contrib.auth.models import User

class Puzzles(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=200, null=True)
	act = models.IntegerField(null=True, default=0)
	scene = models.IntegerField(null=True, default=0)
	pdfPath = models.CharField(max_length=200, null=True)
	answer = models.CharField(max_length=500, null=True)
	winPun = models.CharField(max_length=300, null=True)
	losePun = models.CharField(max_length=300, null=True)
	hint1 = models.CharField(max_length=200, null=True)
	hint2 = models.CharField(max_length=200, null=True)
	hint3 = models.CharField(max_length=200, null=True)
	releaseStatus = models.IntegerField(null=True, default = -1)

	class Meta:
		db_table = 'Puzzles'

class Teams(models.Model):
	id = models.AutoField(primary_key=True)
	authClone = models.ForeignKey(User, models.DO_NOTHING, db_column='authClone', null=True)
	teamName = models.CharField(max_length=50, null=True)
	teamPoints = models.IntegerField(null=True, default=0)

	class Meta:
		db_table = 'Teams'

class SubmittedGuesses(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.ForeignKey(User, models.DO_NOTHING, db_column = 'team', null=True)
	puzzle = models.ForeignKey(Puzzles, models.DO_NOTHING, db_column = 'puzzle', null=True)
	guess = models.CharField(max_length=200, null=True)
	correct = models.BooleanField(null=True)
	submitTime = models.DateTimeField(null=True)

	class Meta:
		db_table = 'SubmittedGuesses'