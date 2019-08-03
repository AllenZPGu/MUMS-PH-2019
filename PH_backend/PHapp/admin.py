from django.contrib import admin
from .models import Puzzles, Teams, SubmittedGuesses, Individuals, AltAnswers, Announcements

# Register your models here.

admin.site.register(Puzzles)
admin.site.register(Teams)
admin.site.register(SubmittedGuesses)
admin.site.register(Individuals)
admin.site.register(AltAnswers)
admin.site.register(Announcements)
