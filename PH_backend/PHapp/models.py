from django.db import models
from django.contrib.auth.models import User

class Puzzles(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=200, null=True)
	act = models.IntegerField(null=True, default=0)
	scene = models.IntegerField(null=True, default=0)
	pdfPath = models.CharField(max_length=200, null=True)
	answers = models.CharField(max_length=500, null=True)
	winPun = models.CharField(max_length=300, null=True)
	losePun = models.CharField(max_length=300, null=True)

	class Meta:
		db_table = 'Puzzles'

class Teams(models.Model):
	id = models.AutoField(primary_key=True)
	authClone = models.ForeignKey(User, models.DO_NOTHING, db_column='scorer', null=True)

	class Meta:
		db_table = 'Scores'