from PHapp.models import Teams, Individuals
from django.contrib.auth.models import User

def run():
	if input('WARNING!!! THIS WILL DELETE A TEAM FOREVER! WOULD YOU LIKE TO PROCEED? ') == "YES":
		teamId = int(input("Team id: "))
		team = Teams.objects.get(id=teamId)
		if input('THIS WILL DELETE THE TEAM    {}    FOREVER! WOULD YOU LIKE TO PROCEED? '.format(team.teamName)) == "YES":
			for i in Individuals.objects.filter(team=teamId):
				print("\tDeleting", i.name)
				i.delete()
			authClone = team.authClone
			print("\tDeleting the team.")
			team.delete()
			authClone.delete()
			print("\tDeleting the username")
			print("Done")

