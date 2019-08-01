from django.contrib import admin
from .models import Puzzles, Teams, SubmittedGuesses, Individuals, AltAnswers

# Register your models here.

admin.site.register(Puzzles)
admin.site.register(Teams)
admin.site.register(SubmittedGuesses)
admin.site.register(Individuals)
admin.site.register(AltAnswers)

