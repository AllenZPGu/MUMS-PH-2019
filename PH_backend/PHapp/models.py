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
    title = models.CharField(max_length=200)
    act = models.IntegerField(null=True, default=0)
    scene = models.IntegerField(null=True, default=0)
    pdfPath = models.CharField(max_length=200, null=True, blank=True)
    answer = models.CharField(max_length=500, null=True, blank=True)
    winPun = models.CharField(max_length=300, null=True, blank=True)
    losePun = models.CharField(max_length=300, null=True, blank=True)
    hint1 = models.CharField(max_length=200, null=True, blank=True)
    hint2 = models.CharField(max_length=200, null=True, blank=True)
    hint3 = models.CharField(max_length=200, null=True, blank=True)
    releaseStatus = models.IntegerField(null=True, default = -1)
    hyperlinkText = models.CharField(max_length=50,editable=False,null=True)
    solveURI = models.CharField(max_length=10,editable=False,null=True)
    pdfURI = models.CharField(max_length=200, null=True, editable=False)
    metaPart1 = models.BooleanField(default=False)
    solveCount = models.IntegerField(default=0)
    guessCount = models.IntegerField(default=0) # Only counts incorrect guesses

    def updateHyperlinkText(self):
        from . helperFunctions import IntToRoman
        if self.act == 7:
            hyperlinkText = 'Meta'
        elif self.scene == 5:
            hyperlinkText = f'Act {IntToRoman(self.act)}, Scene S'
        else:
            hyperlinkText = f'Act {IntToRoman(self.act)}, Scene {self.scene}'
        self.hyperlinkText = hyperlinkText

    def updateSolveURI(self):
        from . helperFunctions import IntToRoman
        if self.act == 7:
            solveURI = 'meta/'
        elif self.scene == 5:
            solveURI = f'{IntToRoman(self.act)}/S/'
        else:
            solveURI = f'{IntToRoman(self.act)}/{self.scene}/'
        self.solveURI = solveURI

    def updatePdfURI(self):
        from . helperFunctions import IntToRoman
        if self.act == 7:
            pdfURI = 'puzzles/Meta.pdf'
        elif self.scene == 5:
            pdfURI = f'puzzles/{IntToRoman(self.act)}.S {self.title}.pdf'
        else:
            pdfURI = f'puzzles/{IntToRoman(self.act)}.{self.scene} {self.title}.pdf'
        self.pdfURI = pdfURI

    def save(self, *args, **kwargs):
        self.updateHyperlinkText()
        self.updateSolveURI()
        self.updatePdfURI()
        super(Puzzles, self).save(*args, **kwargs)

    def __str__(self):
        if self.act == 7:
            if self.scene == 1:
                return 'Meta 1'
            else:
                return 'Meta 2'
        else:
            result = str(self.act)
            if self.scene == 5:
                result = result + '.S'
            else:
                result = result +'.' + str(self.scene)
            return result + ' ' + self.title

    class Meta:
        db_table = 'Puzzles'

class Teams(models.Model):
    id = models.AutoField(primary_key=True)
    authClone = models.OneToOneField(User, models.PROTECT, db_column='authClone', null=True)
    teamName = models.CharField(max_length=50, unique=True, null=True)
    teamPoints = models.IntegerField(default=0)
    teamPuzzles = models.IntegerField(default=0) # number of correct solves
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
    team = models.ForeignKey(Teams, models.PROTECT, db_column='team', null=True)

    class Meta:
        db_table = 'Individuals'

class SubmittedGuesses(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey(User, models.PROTECT, db_column = 'team', null=True)
    puzzle = models.ForeignKey(Puzzles, models.DO_NOTHING, db_column = 'puzzle', null=True)
    guess = models.CharField(max_length=200, null=True)
    correct = models.BooleanField(default = False)
    pointsAwarded = models.IntegerField(null=True)
    submitTime = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'SubmittedGuesses'

class AltAnswers(models.Model):
    id = models.AutoField(primary_key=True)
    puzzle = models.ForeignKey(Puzzles, models.CASCADE, db_column = 'puzzle', null=True)
    altAnswer = models.CharField(max_length=500, null=True)

    class Meta:
        db_table = 'AltAnswers'

class Announcements(models.Model):
    id = models.AutoField(primary_key=True)
    msgTime = models.DateTimeField(auto_now_add=True, null=True)
    msg = models.TextField(max_length=1000, null=True)

    class Meta:
        db_table = 'Announcements'