from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.AltAnswers)
admin.site.register(models.Cubelets)
admin.site.register(models.Individuals)
admin.site.register(models.Puzzles)
admin.site.register(models.SubmittedGuesses)
admin.site.register(models.Teams)