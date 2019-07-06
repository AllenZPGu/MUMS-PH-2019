from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth.models import User
from django.forms import formset_factory, ValidationError
from django.core.mail import send_mail
from .models import Puzzles, Teams, SubmittedGuesses, Individuals, AltAnswers
from .forms import SolveForm, TeamRegForm, IndivRegForm, IndivRegFormSet, LoginForm
from django.conf import settings
import json
import datetime
import pytz
import random
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
import smtplib, ssl
from .helperFunctions import *

aest = pytz.timezone("Australia/Melbourne")
releaseTimes = [aest.localize(datetime.datetime(2019, 8, 7, 12)) + datetime.timedelta(days=i) for i in range(10)]
#releaseTimes = [aest.localize(datetime.datetime(2019, 6, 24, 12)) + datetime.timedelta(days=i) for i in range(10)]

def index(request):
	huntOver = False if releaseStage(releaseTimes) < len(releaseTimes) else True
	return render(request, 'PHapp/home.html', {'huntOver':huntOver})

def colourCube(request):
	huntOver = False if releaseStage(releaseTimes) < len(releaseTimes) else True
	coloured = []
	if request.user.is_authenticated or huntOver:
		if huntOver:
			puzzlesRight = [i for i in Puzzles.objects.all()]
		else:
			puzzlesRight = [i.puzzle for i in SubmittedGuesses.objects.filter(team=request.user, correct=True)]
		
		for rightPuzz in puzzlesRight:
			if rightPuzz.act in range(1,7):
				coloured.append({'cubeletId':rightPuzz.cubelet1.cubeletId, 'cubeface':rightPuzz.cubelet1.cubeface, 'colour':rightPuzz.cubelet1.colour})

	cubeMap = cubeTestRelease(releaseTimes)

	data={'coloured':coloured, 'cubeMap':cubeMap}
	return JsonResponse(data)

@login_required
def puzzles(request):
	puzzleList = []
	for puzzle in Puzzles.objects.filter(releaseStatus__lte = releaseStage(releaseTimes)):
		allGuesses = [i.correct for i in SubmittedGuesses.objects.filter(puzzle=puzzle)]

		guesses = SubmittedGuesses.objects.filter(puzzle=puzzle, team=request.user)

		if True not in [i.correct for i in guesses]:
			puzzleList.append([puzzle, False, sum(allGuesses), len(allGuesses)-sum(allGuesses), calcWorth(puzzle, releaseTimes)])
		else:
			correctGuess = guesses.filter(correct = True)[0]
			puzzleList.append([puzzle, True, sum(allGuesses), len(allGuesses)-sum(allGuesses), correctGuess.pointsAwarded])
	puzzleList = sorted(puzzleList, key=lambda x:x[0].id)

	nextRelease = calcNextRelease(releaseTimes)
	print(nextRelease)

	return render(request, 'PHapp/puzzles.html', {'puzzleList':puzzleList, 'nextRelease':nextRelease})

@login_required
def puzzleInfo(request, title):
	try:
		puzzle = Puzzles.objects.get(pdfPath=title)
	except:
		raise Http404()
	if releaseStage(releaseTimes) < puzzle.releaseStatus:
		raise Http404()

	allGuesses = SubmittedGuesses.objects.filter(puzzle=puzzle)
	allSolves = sorted([[i, calcSingleTime(i, i.submitTime, releaseTimes)[0]] for i in allGuesses if i.correct], key=lambda x:x[0].submitTime)
	
	totalRight = len(allSolves)
	totalWrong = len(allGuesses) - totalRight

	return render(request, 'PHapp/puzzleStats.html', 
		{'puzzle':puzzle, 'allSolves':allSolves, 'totalWrong':totalWrong, 'totalRight':totalRight, 'avTime':calcPuzzleTime(puzzle, releaseTimes)[0]})

@login_required
def showPuzzle(request, puzzleURL):
	try:
		puzzle = Puzzles.objects.get(pdfPath=puzzleURL.replace('.pdf', ''))
	except:
		raise Http404()
	if releaseStage(releaseTimes) < puzzle.releaseStatus:
		raise Http404()
	try:
		return FileResponse(open(os.path.join(settings.BASE_DIR, 'PHapp/puzzleFiles/', puzzleURL), 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404("PDF file not found at "+os.path.join(settings.BASE_DIR, 'PHapp/puzzleFiles/', puzzleURL))

@login_required
def solve(request, title):
	try:
		puzzle = Puzzles.objects.get(pdfPath=title)
	except:
		raise Http404()
	if releaseStage(releaseTimes) < puzzle.releaseStatus:
		raise Http404()
	
	team = Teams.objects.get(authClone = request.user)
	guesses = SubmittedGuesses.objects.filter(team = request.user, puzzle = puzzle)
	if True in [i.correct for i in guesses]:
		correctGuess = guesses.filter(correct=True)[0]
		points = correctGuess.pointsAwarded
		if correctGuess.guess != puzzle.answer:
			altAns = correctGuess.guess
		else:
			altAns = None
		return render(request, 'PHapp/solveCorrect.html', {'puzzle':puzzle, 'points':points, 'team':team, 'altAns':altAns})

	if team.guesses <= 0:
		return render(request, 'PHapp/noGuesses.html')

	if request.method == 'POST':
		solveform = SolveForm(request.POST)
		if solveform.is_valid():
			guess = stripToLetters(solveform.cleaned_data['guess'])
			altAnswersList = [i.altAnswer for i in AltAnswers.objects.filter(puzzle=puzzle)]
			

			if guess == puzzle.answer or guess in altAnswersList:
				newSubmit = SubmittedGuesses()
				newSubmit.team = request.user
				newSubmit.puzzle = puzzle
				newSubmit.guess = guess
				newSubmit.submitTime = aest.localize(datetime.datetime.now())
				newSubmit.correct = True
				newSubmit.pointsAwarded = calcWorth(puzzle, releaseTimes)
				newSubmit.save()

				solveTime = calcSolveTime(team, releaseTimes)
				team.avHr = solveTime[1]
				team.avMin = solveTime[2]
				team.avSec = solveTime[3]
				team.teamPoints += calcWorth(puzzle, releaseTimes)
				team.teamPuzzles += 1
				team.save()

				webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
				webhookTitle = '**{}** solved **{}.{} {}**'.format(team.teamName, puzzle.act, puzzle.scene, puzzle.title)
				webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
				webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=47872)
				webhook.add_embed(webhookEmbed)
				webhook.execute()

				return redirect('/solve/{}/'.format(title))

			else:
				if len(SubmittedGuesses.objects.filter(guess=guess, puzzle=puzzle, team=team.authClone)) == 0:
					newSubmit = SubmittedGuesses()
					newSubmit.team = request.user
					newSubmit.puzzle = puzzle
					newSubmit.guess = guess
					newSubmit.submitTime = aest.localize(datetime.datetime.now())
					newSubmit.correct = False
					newSubmit.save()
					team.guesses -= 1
					team.save()
					displayWrong = True
					displayDouble = False
					displayGuess = None

				else:
					displayWrong = False
					displayDouble = True
					displayGuess = guess

				webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
				webhookTitle = '**{}** incorrectly attempted **{}.{} {}**'.format(team.teamName, puzzle.act, puzzle.scene, puzzle.title)
				webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
				webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=12255232)
				webhook.add_embed(webhookEmbed)
				webhook.execute()

				solveform = SolveForm()

	else:
		solveform = SolveForm()
		displayWrong = False
		displayDouble = False
		displayGuess = None

	previousGuesses = [i.guess for i in SubmittedGuesses.objects.filter(puzzle=puzzle, team=team.authClone, correct=False)]
	previousGuesses = sorted(previousGuesses)

	return render(request, 'PHapp/solve.html', 
		{'solveform':solveform, 'displayWrong':displayWrong, 'displayDouble':displayDouble, 'displayGuess':displayGuess, 'puzzle':puzzle, 'team':team, 'previousGuesses':previousGuesses})

def teams(request):
	if len(Teams.objects.all()) == 0:
		return render(request, 'PHapp/teams.html', {'teamsExist':False})

	allTeams = []
	totRank = 1
	ausRank = 1

	teamsWithSolves = Teams.objects.filter(teamPoints__gt=0)
	for team in teamsWithSolves:
		allTeams.append([team, "{:02d}h {:02d}m {:02d}s".format(team.avHr, team.avMin, team.avSec), team.avHr, team.avMin, team.avSec])

	allTeams = sorted(allTeams, key=lambda x:x[0].id) #sort by ID
	allTeams = sorted(allTeams, key=lambda x:3600*x[2]+60*x[3]+x[4]) #sort by average solve time
	allTeams = sorted(allTeams, key=lambda x:-x[0].teamPuzzles) #sort by team puzzles
	allTeams = sorted(allTeams, key=lambda x:-x[0].teamPoints) #sort by team points

	for i in range(len(allTeams)):
		allTeams[i].append(totRank)
		totRank += 1
		if allTeams[i][0].aussie:
			allTeams[i].append(ausRank)
			ausRank += 1
		else:
			allTeams[i].append('-')

	teamsWithoutSolves = Teams.objects.filter(teamPoints=0)
	allTeams += sorted([[team, '-', None, None, None, '-', '-'] for team in teamsWithoutSolves], key=lambda x:x[0].id)

	teamName = None
	if request.user.is_authenticated:
		teamName = Teams.objects.get(authClone = request.user).teamName
	
	return render(request, 'PHapp/teams.html', {'allTeams':allTeams, 'teamName':teamName, 'teamsExist':True})

def teamReg(request):
	if request.user.is_authenticated:
		return redirect('/')

	if request.method == 'POST':
		userForm = UserCreationForm(request.POST)
		regForm = TeamRegForm(request.POST)
		indivFormSet = IndivRegFormSet(request.POST)

		if userForm.is_valid() and indivFormSet.is_valid() and regForm.is_valid():
			userForm.save()

			username = userForm.cleaned_data.get('username')
			raw_password = userForm.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)

			newTeam = regForm.save()
			newTeam.authClone = user
			newTeam.save()
			newTeam.aussie = False
			
			recipient_list = [] if newTeam.teamEmail == '' else [newTeam.teamEmail]
			indivNo = 0

			for indivForm in indivFormSet:
				if indivForm.cleaned_data.get('name') == None:
					continue
				newIndiv = Individuals()
				newIndiv.name = indivForm.cleaned_data.get('name')
				newIndiv.email = indivForm.cleaned_data.get('email')
				newIndiv.aussie = indivForm.cleaned_data.get('aussie')
				newIndiv.melb = indivForm.cleaned_data.get('melb')
				newIndiv.team = newTeam
				newIndiv.save()
				if newIndiv.aussie:
					newTeam.aussie = True

				recipient_list.append(newIndiv.email)
				indivNo += 1

			newTeam.save()

			try:
				msg_username = 'Username: ' + username + '\n'
				msg_name = 'Team name: ' + newTeam.teamName + '\n\n'
			
				# message = 'Thank you for registering for the 2019 MUMS Puzzle Hunt. Please find below your team details:\n\n' + msg_username + msg_name + 'A reminder that you will need your username, and not your team name, to login.\n\n' + 'Regards,\n' + 'MUMS Puzzle Hunt Organisers'
				# subject = '[PH2019] Team registered'
				# email_from = settings.EMAIL_HOST_USER
				# send_mail( subject, message, email_from, recipient_list )

			
				message = 'Subject: [PH2019] Team registered\n\nThank you for registering for the 2019 MUMS Puzzle Hunt. Please find below your team details:\n\n' + msg_username + msg_name + 'A reminder that you will need your username, and not your team name, to login.\n\n' + 'Regards,\n' + 'MUMS Puzzle Hunt Organisers'
				context = ssl.create_default_context()
				with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as emailServer:
					emailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
					emailServer.sendmail(settings.EMAIL_HOST_USER, recipient_list, message)
			except:
				pass

			webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
			webhookTitle = 'New team: **{}**'.format(newTeam.teamName)
			webhookDesc = 'Members: {}\nAustralian: {}'.format(str(indivNo), 'Yes' if newTeam.aussie else 'No')
			webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=16233769)
			webhook.add_embed(webhookEmbed)
			webhook.execute()

			return redirect('/team/{}'.format(str(newTeam.id)))
	
	else:
		userForm = UserCreationForm()
		regForm = TeamRegForm()
		indivFormSet = IndivRegFormSet()
	return render(request, 'PHapp/teamReg.html', {'userForm':userForm, 'regForm':regForm, 'indivFormSet':indivFormSet})

def teamInfo(request, teamId):
	team = Teams.objects.get(id=teamId)
	membersList = sorted([i for i in Individuals.objects.filter(team=team)], key=lambda x:x.name)
	correctList = [[i, calcSingleTime(i, i.submitTime, releaseTimes)[0], len(SubmittedGuesses.objects.filter(team=team.authClone, correct=False, puzzle=i.puzzle))] for i in SubmittedGuesses.objects.filter(team=team.authClone, correct=True)]
	correctList = sorted(correctList, key=lambda x:x[0].submitTime)
	anySolves = True if len(correctList) > 0 else False
	avSolveTime = "{:02d}h {:02d}m {:02d}s".format(team.avHr, team.avMin, team.avSec) if anySolves else 'N/A'
	return render(request, 'PHapp/teamInfo.html', {'team':team, 'members':membersList, 'correctList':correctList, 'anySolves':anySolves, 'avSolveTime':avSolveTime})

@login_required
def hints(request, title):
	try:
		puzzle = Puzzles.objects.get(pdfPath=title)
	except:
		raise Http404()
	if releaseStage(releaseTimes) < puzzle.releaseStatus:
		raise Http404()

	toRender = []
	anyHints = False
	nextHint = releaseTimes[puzzle.releaseStatus]
	if releaseStage(releaseTimes) - puzzle.releaseStatus >= 1:
		toRender.append([1, puzzle.hint1])
		anyHints = True
		nextHint = releaseTimes[puzzle.releaseStatus + 1]
	if releaseStage(releaseTimes) - puzzle.releaseStatus >= 2:
		toRender.append([2, puzzle.hint2])
		nextHint = releaseTimes[puzzle.releaseStatus + 2]
	if releaseStage(releaseTimes) - puzzle.releaseStatus >= 3:
		toRender.append([3, puzzle.hint3])
		nextHint = None
	return render(request, 'PHapp/hints.html', {'toRender':toRender, 'anyHints':anyHints, 'nextHint':nextHint, 'puzzle':puzzle})

def faq(request):
	return render(request, 'PHapp/faq.html')

def rules(request):
	return render(request, 'PHapp/rules.html')

def debrief(request):
	if not huntFinished(releaseTimes):
		raise Http404()
	else:
		return render(request, 'PHapp/home.html')

def loginCustom(request):
	if request.user.is_authenticated:
		return redirect('/')

	if request.method == 'POST':
		loginForm = LoginForm(request.POST)
		if loginForm.is_valid():
			username = loginForm.cleaned_data.get('username')
			password = loginForm.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			
			if user == None:
				loginForm = LoginForm()
				return render(request, 'PHapp/login.html', {'loginForm':loginForm, 'wrong':True})
			else:
				login(request, user)
				return redirect('/')
	else:
		loginForm = LoginForm()

	return render(request, 'PHapp/login.html', {'loginForm':loginForm, 'wrong':False})

def logoutCustom(request):
	logout(request)
	return redirect('/')