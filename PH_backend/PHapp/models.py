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

class Individuals(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100, null=True)
	email = models.EmailField(max_length=254, null=True)
	aussie = models.BooleanField(null=True)
	melb = models.BooleanField(null=True)

	class Meta:
		db_table = 'Individuals'

class Teams(models.Model):
	id = models.AutoField(primary_key=True)
	authClone = models.ForeignKey(User, models.DO_NOTHING, db_column='authClone', null=True)
	teamName = models.CharField(max_length=50, null=True)
	teamPoints = models.IntegerField(default=0)
	teamEmail = models.EmailField(max_length=254, null=True)
	member1 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member1', related_name='member1', null=True)
	member2 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member2', related_name='member2',null=True)
	member3 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member3', related_name='member3',null=True)
	member4 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member4', related_name='member4',null=True)
	member5 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member5', related_name='member5',null=True)
	member6 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member6', related_name='member6',null=True)
	member7 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member7', related_name='member7',null=True)
	member8 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member8', related_name='member8',null=True)
	member9 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member9', related_name='member9',null=True)
	member10 = models.ForeignKey(Individuals, models.DO_NOTHING, db_column='member10', related_name='member10',null=True)

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