from PHapp.models import SubmittedGuesses, Teams, Puzzles

def run():
	if input("CHECK THAT YOUR DATABASE IS NOT CONNECTED TO LIVE!!!!!!!!! ") == "Y":
		SubmittedGuesses.objects.all().delete()
		Teams.objects.all().update(teamPoints=0, teamPuzzles=0, avHr=None, avMin=None, avSec=None, guesses=100)
		Puzzles.objects.all().update(solveCount=0, guessCount=0)