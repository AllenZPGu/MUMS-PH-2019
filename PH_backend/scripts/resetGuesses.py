from PHapp.models import Teams

def run():
	Teams.objects.all().update(guesses=100)