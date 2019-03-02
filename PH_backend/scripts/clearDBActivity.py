from PHapp.models import SubmittedGuesses, Teams

def run():
	SubmittedGuesses.objects.all().delete()
	Teams.objects.all().update(teamPoints=0, teamPuzzles=0, avHr=None, avMin=None, avSec=None, guesses=100)