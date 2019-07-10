from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.contrib.auth.models import User
from django.forms import formset_factory, ValidationError
from django.core.mail import send_mail
from django.views.decorators.http import last_modified
from .models import Puzzles, Teams, SubmittedGuesses, Individuals, AltAnswers
from .forms import SolveForm, TeamRegForm, IndivRegForm, IndivRegFormSet, LoginForm, BaseIndivRegFormSet
from django.conf import settings
import json
import datetime
import pytz
import random
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
import smtplib, ssl
from .helperFunctions import *

AEST = pytz.timezone("Australia/Melbourne")
RELEASETIMES = [AEST.localize(datetime.datetime(2019, 8, 7, 12)) + datetime.timedelta(days=i) for i in range(10)]
PUZZLECOLOURS = [
	['W','O','','','G','',], ['O','W','','','','',], ['W','O','B','','','',],
	['Y','','','','O','',],  ['R','','','','','',],  ['G','','O','','','',],
	['B','','','Y','R','',], ['G','','','Y','','',], ['W','','R','G','','',],
	['','W','','','B','',],  ['','B','','','','',],  ['','B','R','','','',],
	['','','','','W','',],   ['','','','','','',],   ['','','Y','','','',],
	['','','','R','Y','',],  ['','','','G','','',],  ['','','B','O','','',],
	['','Y','','','O','G',], ['','G','','','','R',], ['','W','R','','','B',],
	['','','','','G','W',],  ['','','','','','O',],  ['','','W','','','R',],
	['','','','O','B','Y',], ['','','','B','','Y',], ['','','Y','R','','G',],
]
PUZZLECOLOURSBLANK = [
	['A','A','','','A','',], ['A','A','','','','',], ['A','A','A','','','',],
	['A','','','','A','',],  ['A','','','','','',],  ['A','','A','','','',],
	['A','','','A','A','',], ['A','','','A','','',], ['A','','A','A','','',],
	['','A','','','A','',],  ['','A','','','','',],  ['','A','A','','','',],
	['','','','','A','',],   ['','','','','','',],   ['','','A','','','',],
	['','','','A','A','',],  ['','','','A','','',],  ['','','A','A','','',],
	['','A','','','A','A',], ['','A','','','','A',], ['','A','A','','','A',],
	['','','','','A','A',],  ['','','','','','A',],  ['','','A','','','A',],
	['','','','A','A','A',], ['','','','A','','A',], ['','','A','A','','A',],
]
PUZZLETEXTS = [
	['1','3','','','2','',], ['','','','','','',],   ['2','4','1','','','',],
	['','','','','','',],    ['I','','','','','',],  ['','','','','','',],
	['3','','','1','4','',], ['','','','','','',],   ['4','','3','2','','',],
	['','','','','','',],    ['','V','','','','',],  ['','','','','','',],
	['','','','','VI',''],   ['','','','','','',],   ['','','III','','','',],
	['','','','','','',],    ['','','','IV','','',], ['','','','','','',],
	['','1','','','1','2',], ['','','','','','',],   ['','2','2','','','1',],
	['','','','','','',],    ['','','','','','II',], ['','','','','','',],
	['','','','3','3','4',], ['','','','','','',],   ['','','4','4','','2',],
]

#releaseTimes = [aest.localize(datetime.datetime(2019, 6, 24, 12)) + datetime.timedelta(days=i) for i in range(10)]

def index(request):
	huntOver = (releaseStage(RELEASETIMES) > len(RELEASETIMES))
	return render(request, 'PHapp/home.html', {'huntOver':huntOver})

def IsMeta(puzzle):
	return (puzzle.act == 7)

def IsMetaOrMiniMeta(puzzle):
	return (IsMeta(puzzle) or puzzle.scene == 5)

def cubeDataColourCell(puzzle):
	if IsMeta(puzzle):
		return None
	return ((),
			((),  (0, 0),  (2, 0),  (6, 0),  (8, 0),  (4, 0)),
			((), (20, 5), (18, 5), (26, 5), (24, 5), (22, 5)),
			((),  (2, 2), (20, 2),  (8, 2), (26, 2), (14, 2)),
			((),  (6, 3),  (8, 3), (24, 3), (26, 3), (16, 3)),
			((), (18, 1), (20, 1),  (0, 1),  (2, 1), (10, 1)),
			((), (18, 4),  (0, 4), (24, 4),  (6, 4), (12, 4)))[puzzle.act][puzzle.scene]


def cubeDataLastModified(request):
	
	# TODO: test this
	if request.user.is_authenticated:
		guesses = SubmittedGuesses.objects.filter(team=request.user).filter(correct=True)
		if guesses: 
			return guesses.latest.submitTime
	elif releaseStage(RELEASETIMES) > len(RELEASETIMES):
		# hunt is over; check that this time is kosher
		return RELEASETIMES[-1]
	# Default case
	return AEST.localize(datetime.datetime(2019, 7, 9))
		
@last_modified(cubeDataLastModified)
def cubeData(request):
	huntOver = (releaseStage(RELEASETIMES) > len(RELEASETIMES))
	responseData = [{'colors': PUZZLECOLOURSBLANK[i], 'text': ['']*6, 'links': ['']*6} for i in range(27)]
	if request.user.is_authenticated:
		puzzlesRight = [i.puzzle for i in SubmittedGuesses.objects.filter(team=request.user, correct=True)]

		metascomplete = [False] * 8

		# colour the response
		for rightPuzz in puzzlesRight:
			if IsMetaOrMiniMeta(puzzle):
				metascomplete[puzzle.scene] = True
			if not IsMeta(puzzle):
				colourcell = cubeDataColourCell(puzzle)
				if colourcell:
					responseData[colourcell[0]]['colors'][colourcell[1]] = PUZZLECOLOURS[colourcell[0]][colourcell[1]]
		if metascomplete[7]:
			# Meta 1 is done (and maybe 2, but we'll check that now)
			if puzzlesRight.filter(puzzle__act=7).filter(puzzle__scene=2):
				# Meta 2 is done; set up to colour the whole cube
				metascomplete = [True] * 8
			if metascomplete[1]:
				for i in range(9):
					responseData[i]['colors'][0] = PUZZLECOLOURS[i][0]
			if metascomplete[2]:
				for i in range(18, 27):
					responseData[i]['colors'][5] = PUZZLECOLOURS[i][5]
			if metascomplete[3]:
				for i in range(2, 27, 3):
					responseData[i]['colors'][2] = PUZZLECOLOURS[i][2]
			if metascomplete[4]:
				for i in range(6,9):
					for j in range(3):
						k = i + 9*j
						responseData[k]['colors'][3] = PUZZLECOLOURS[k][3]
			if metascomplete[5]:
				for i in range(3):
					for j in range(3):
						k = i + 9*j
						responseData[k]['colors'][1] = PUZZLECOLOURS[k][1]
			if metascomplete[6]:
				for i in range(0, 25, 3):
					responseData[i]['colors'][4] = PUZZLECOLOURS[i][4]
	availablePuzzles = Puzzles.objects.filter(releaseStatus__lte = releaseStage(RELEASETIMES))
	for puzzle in availablePuzzles:
		if not IsMeta(puzzle):
			colourcell = cubeDataColourCell(puzzle)
			responseData[colourcell[0]]['links'][colourcell[1]] = puzzle.pdfPath
			responseData[colourcell[0]]['text'][colourcell[1]] = PUZZLETEXTS[colourcell[0]][colourcell[1]]

	return HttpResponse('window.rawcubedata=' + json.dumps(responseData,separators=(',', ':')), content_type='application/javascript')

@login_required
def puzzles(request):
	puzzleList = []
	for puzzle in Puzzles.objects.filter(releaseStatus__lte = releaseStage(RELEASETIMES)):
		allGuesses = [i.correct for i in SubmittedGuesses.objects.filter(puzzle=puzzle)]

		guesses = SubmittedGuesses.objects.filter(puzzle=puzzle, team=request.user)

		if True not in [i.correct for i in guesses]:
			puzzleList.append([puzzle, False, sum(allGuesses), len(allGuesses)-sum(allGuesses), calcWorth(puzzle, RELEASETIMES)])
		else:
			correctGuess = guesses.filter(correct = True)[0]
			puzzleList.append([puzzle, True, sum(allGuesses), len(allGuesses)-sum(allGuesses), correctGuess.pointsAwarded])
	puzzleList = sorted(puzzleList, key=lambda x:x[0].id)

	nextRelease = calcNextRelease(RELEASETIMES)
	print(nextRelease)

	return render(request, 'PHapp/puzzles.html', {'puzzleList':puzzleList, 'nextRelease':nextRelease})

@login_required
def puzzleInfo(request, title):
	try:
		puzzle = Puzzles.objects.get(pdfPath=title)
	except:
		raise Http404()
	if releaseStage(RELEASETIMES) < puzzle.releaseStatus:
		raise Http404()

	allGuesses = SubmittedGuesses.objects.filter(puzzle=puzzle)
	allSolves = sorted([[i, calcSingleTime(i, i.submitTime, RELEASETIMES)[0]] for i in allGuesses if i.correct], key=lambda x:x[0].submitTime)
	
	totalRight = len(allSolves)
	totalWrong = len(allGuesses) - totalRight

	return render(request, 'PHapp/puzzleStats.html', 
		{'puzzle':puzzle, 'allSolves':allSolves, 'totalWrong':totalWrong, 'totalRight':totalRight, 'avTime':calcPuzzleTime(puzzle, RELEASETIMES)[0]})

def showPuzzle(request, puzzleURL):
	try:
		puzzle = Puzzles.objects.get(pdfPath=puzzleURL.replace('.pdf', ''))
	except:
		raise Http404()
	if releaseStage(RELEASETIMES) < puzzle.releaseStatus:
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
	if releaseStage(RELEASETIMES) < puzzle.releaseStatus:
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
				newSubmit.submitTime = AEST.localize(datetime.datetime.now())
				newSubmit.correct = True
				newSubmit.pointsAwarded = calcWorth(puzzle, RELEASETIMES)
				newSubmit.save()

				solveTime = calcSolveTime(team, RELEASETIMES)
				team.avHr = solveTime[1]
				team.avMin = solveTime[2]
				team.avSec = solveTime[3]
				team.teamPoints += calcWorth(puzzle, RELEASETIMES)
				team.teamPuzzles += 1
				team.save()

				try:
					webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
					webhookTitle = '**{}** solved **{}.{} {}**'.format(team.teamName, puzzle.act, puzzle.scene, puzzle.title)
					webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
					webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=47872)
					webhook.add_embed(webhookEmbed)
					webhook.execute()
				except:
					pass

				return redirect('/solve/{}/'.format(title))

			else:
				if len(SubmittedGuesses.objects.filter(guess=guess, puzzle=puzzle, team=team.authClone)) == 0:
					newSubmit = SubmittedGuesses()
					newSubmit.team = request.user
					newSubmit.puzzle = puzzle
					newSubmit.guess = guess
					newSubmit.submitTime = AEST.localize(datetime.datetime.now())
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

				try:
					webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
					webhookTitle = '**{}** incorrectly attempted **{}.{} {}**'.format(team.teamName, puzzle.act, puzzle.scene, puzzle.title)
					webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
					webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=12255232)
					webhook.add_embed(webhookEmbed)
					webhook.execute()
				except:
					pass

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

			
				message = 'Subject: [MPH 2019] Team registered\n\nThank you for registering for the 2019 MUMS Puzzle Hunt. Please find below your team details:\n\n' + msg_username + msg_name + 'A reminder that you will need your username, and not your team name, to login.\n\n' + 'Regards,\n' + 'MUMS Puzzle Hunt Organisers'
				context = ssl.create_default_context()
				with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as emailServer:
					emailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
					emailServer.sendmail(settings.EMAIL_HOST_USER, recipient_list, message)
			except:
				pass

			try:
				webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
				webhookTitle = 'New team: **{}**'.format(newTeam.teamName)
				webhookDesc = 'Usename: {}\nMembers: {}\nAustralian: {}'.format(username, str(indivNo), 'Yes' if newTeam.aussie else 'No')
				webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=16233769)
				webhook.add_embed(webhookEmbed)
				webhook.execute()
			except:
				pass

			return redirect('/team/{}'.format(str(newTeam.id)))
	
	else:
		userForm = UserCreationForm()
		regForm = TeamRegForm()
		indivFormSet = IndivRegFormSet()
	return render(request, 'PHapp/teamReg.html', {'userForm':userForm, 'regForm':regForm, 'indivFormSet':indivFormSet})


@login_required
def editTeamMembers(request):
	team = Teams.objects.get(authClone = request.user)
	existing = len(Individuals.objects.filter(team=team))
	if existing >= 10:
		return render(request, 'PHapp/editTeam.html', {'canEdit':False, 'team':team})

	EditFormSet = forms.formset_factory(IndivRegForm, formset=BaseIndivRegFormSet, extra=10-existing)

	if request.method == 'POST':
		indivFormSet = EditFormSet(request.POST)

		if indivFormSet.is_valid():
			for indivForm in indivFormSet:
				if indivForm.cleaned_data.get('name') == None:
					continue
				newIndiv = Individuals()
				newIndiv.name = indivForm.cleaned_data.get('name')
				newIndiv.email = indivForm.cleaned_data.get('email')
				newIndiv.aussie = indivForm.cleaned_data.get('aussie')
				newIndiv.melb = indivForm.cleaned_data.get('melb')
				newIndiv.team = team
				newIndiv.save()
				if newIndiv.aussie:
					team.aussie = True

			team.save()

			return redirect('/team/{}'.format(str(team.id)))
	
	else:
		indivFormSet = EditFormSet()
	return render(request, 'PHapp/editTeam.html', {'canEdit':True, 'indivFormSet':indivFormSet, 'team':team, 'extra':10-existing})


def teamInfo(request, teamId):
	team = Teams.objects.get(id=teamId)
	membersList = sorted([i for i in Individuals.objects.filter(team=team)], key=lambda x:x.name)
	correctList = [[i, calcSingleTime(i, i.submitTime, RELEASETIMES)[0], len(SubmittedGuesses.objects.filter(team=team.authClone, correct=False, puzzle=i.puzzle))] for i in SubmittedGuesses.objects.filter(team=team.authClone, correct=True)]
	correctList = sorted(correctList, key=lambda x:x[0].submitTime)
	anySolves = True if len(correctList) > 0 else False
	avSolveTime = "{:02d}h {:02d}m {:02d}s".format(team.avHr, team.avMin, team.avSec) if anySolves else 'N/A'
	return render(request, 'PHapp/teamInfo.html', {'team':team, 'members':membersList, 'donation':str(len(membersList)*2),'correctList':correctList, 'anySolves':anySolves, 'avSolveTime':avSolveTime})

@login_required
def hints(request, title):
	try:
		puzzle = Puzzles.objects.get(pdfPath=title)
	except:
		raise Http404()
	if releaseStage(RELEASETIMES) < puzzle.releaseStatus:
		raise Http404()

	toRender = []
	anyHints = False
	nextHint = RELEASETIMES[puzzle.releaseStatus]
	if releaseStage(RELEASETIMES) - puzzle.releaseStatus >= 1:
		toRender.append([1, puzzle.hint1])
		anyHints = True
		nextHint = RELEASETIMES[puzzle.releaseStatus + 1]
	if releaseStage(RELEASETIMES) - puzzle.releaseStatus >= 2:
		toRender.append([2, puzzle.hint2])
		nextHint = RELEASETIMES[puzzle.releaseStatus + 2]
	if releaseStage(RELEASETIMES) - puzzle.releaseStatus >= 3:
		toRender.append([3, puzzle.hint3])
		nextHint = None
	return render(request, 'PHapp/hints.html', {'toRender':toRender, 'anyHints':anyHints, 'nextHint':nextHint, 'puzzle':puzzle})

def faq(request):
	return render(request, 'PHapp/faq.html')

def rules(request):
	return render(request, 'PHapp/rules.html')

def debrief(request):
	if not huntFinished(RELEASETIMES):
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