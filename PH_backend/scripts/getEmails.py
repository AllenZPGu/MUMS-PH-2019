from PHapp.models import Teams, Individuals

def run():
	with open('../emails.csv', 'w') as f:
		f.write('Name,Email\n')
		for i in Teams.objects.exclude(teamEmail = None):
			try:
				f.write('Team {},{}\n'.format(i.teamName.replace(',',''), i.teamEmail))
			except:
				f.write('Team {},{}\n'.format(i.id, i.teamEmail))
		for i in Individuals.objects.all():
			try:
				f.write('{},{}\n'.format(i.name.replace(',',''), i.email))
			except:
				f.write('Team {},{}\n'.format(i.id, i.email))