from django.db import models
from django.contrib.auth.models import User

class Cubelets(models.Model):
	id = models.AutoField(primary_key=True)
	cubeletId = models.IntegerField(null=True)
	cubeface = models.IntegerField(null=True)
	colour = models.CharField(max_length=1, null=True)

	class Meta:
		db_table = 'Cubelets'

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
	cubelet1 = models.ForeignKey(Cubelets, models.DO_NOTHING, db_column='cubelet1', related_name='cubelet1', null=True)

	class Meta:
		db_table = 'Puzzles'

class Teams(models.Model):
	id = models.AutoField(primary_key=True)
	authClone = models.ForeignKey(User, models.DO_NOTHING, db_column='authClone', null=True)
	teamName = models.CharField(max_length=50, unique=True, null=True)
	teamPoints = models.IntegerField(default=0)
	teamPuzzles = models.IntegerField(default=0)
	teamEmail = models.EmailField(max_length=254, null=True, blank=True, unique=True)
	aussie = models.BooleanField(default=False)
	avHr = models.IntegerField(null=True)
	avMin = models.IntegerField(null=True)
	avSec = models.IntegerField(null=True)
	guesses = models.IntegerField(default=100)

	class Meta:
		db_table = 'Teams'

class Individuals(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100, null=True)
	email = models.EmailField(max_length=254, null=True)
	aussie = models.BooleanField(default = False)
	melb = models.BooleanField(default = False)
	team = models.ForeignKey(Teams, models.DO_NOTHING, db_column='team', null=True)

	class Meta:
		db_table = 'Individuals'

class SubmittedGuesses(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.ForeignKey(User, models.DO_NOTHING, db_column = 'team', null=True)
	puzzle = models.ForeignKey(Puzzles, models.DO_NOTHING, db_column = 'puzzle', null=True)
	guess = models.CharField(max_length=200, null=True)
	correct = models.BooleanField(default = False)
	pointsAwarded = models.IntegerField(null=True)
	submitTime = models.DateTimeField(null=True)

	class Meta:
		db_table = 'SubmittedGuesses'

class AltAnswers(models.Model):
	id = models.AutoField(primary_key=True)
	puzzle = models.ForeignKey(Puzzles, models.DO_NOTHING, db_column = 'puzzle', null=True)
	altAnswer = models.CharField(max_length=500, null=True)

	class Meta:
		db_table = 'AltAnswers'