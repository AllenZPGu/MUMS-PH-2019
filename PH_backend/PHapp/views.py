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
from django.urls import reverse
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
from .globals import *

# Force rebuild

SOLVE_WRONG = 0
SOLVE_DUPLICATE = 1
SOLVE_METAHALF = 2
SOLVE_METAHALFDUPLICATE = 3

#releaseTimes = [aest.localize(datetime.datetime(2019, 6, 24, 12)) + datetime.timedelta(days=i) for i in range(10)]

def index(request):
	huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
	return render(request, 'PHapp/home.html', {'huntOver':huntOver})

def cubeDataLastModified(request):
	# TODO: test this
	if request.user.is_authenticated:
		guesses = SubmittedGuesses.objects.filter(team=request.user).filter(correct=True)
		if guesses: 
			return max(guesses.latest('submitTime').submitTime, RELEASE_TIMES[releaseStage(RELEASE_TIMES)])
	if releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES):
		# hunt is over; check that this time is kosher
		return RELEASE_TIMES[-1]
	# Default case
	return None

#@last_modified(cubeDataLastModified)
def cubeData(request):
	huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
	responseData = [{'colors': PUZZLE_COLOURS_BLANK[i], 'text': ['']*6, 'links': ['']*6} for i in range(27)]
	if request.user.is_authenticated:
		correctGuesses = SubmittedGuesses.objects.filter(team=request.user, correct=True)

		metascomplete = [False] * 8

		# colour the response
		for guess in correctGuesses:
			puzzle = guess.puzzle
			if IsMetaOrMiniMeta(puzzle):
				metascomplete[puzzle.act] = True
			if not IsMeta(puzzle):
				colourcell = cubeDataColourCell(puzzle)
				if colourcell:
					responseData[colourcell[0]]['colors'][colourcell[1]] = PUZZLE_COLOURS[colourcell[0]][colourcell[1]]
		if metascomplete[7]:
			# Meta 1 is done (and maybe 2, but we'll check that now)
			if correctGuesses.filter(puzzle__act=7).filter(puzzle__scene=2):
				# Meta 2 is done; set up to colour the whole cube
				metascomplete = [True] * 8
			if metascomplete[1]:
				for i in range(9):
					responseData[i]['colors'][0] = PUZZLE_COLOURS[i][0]
			if metascomplete[2]:
				for i in range(18, 27):
					responseData[i]['colors'][5] = PUZZLE_COLOURS[i][5]
			if metascomplete[3]:
				for i in range(2, 27, 3):
					responseData[i]['colors'][2] = PUZZLE_COLOURS[i][2]
			if metascomplete[4]:
				for i in range(6,9):
					for j in range(3):
						k = i + 9*j
						responseData[k]['colors'][3] = PUZZLE_COLOURS[k][3]
			if metascomplete[5]:
				for i in range(3):
					for j in range(3):
						k = i + 9*j
						responseData[k]['colors'][1] = PUZZLE_COLOURS[k][1]
			if metascomplete[6]:
				for i in range(0, 25, 3):
					responseData[i]['colors'][4] = PUZZLE_COLOURS[i][4]
	availablePuzzles = Puzzles.objects.filter(releaseStatus__lte = releaseStage(RELEASE_TIMES))
	for puzzle in availablePuzzles:
		if not IsMeta(puzzle):
			colourcell = cubeDataColourCell(puzzle)
			responseData[colourcell[0]]['links'][colourcell[1]] = reverse(showPuzzle, kwargs={'act': IntToRoman(puzzle.act), 'scene': puzzle.scene, 'puzzleName': puzzle.title})
			responseData[colourcell[0]]['text'][colourcell[1]] = PUZZLE_TEXTS[colourcell[0]][colourcell[1]]

	return HttpResponse('window.rawcubedata=' + json.dumps(responseData,separators=(',', ':')), content_type='application/javascript')

def puzzles(request):
	puzzleList = []
	if request.user.is_authenticated:
		userCorrectGuesses = SubmittedGuesses.objects.filter(correct=True).filter(team=request.user)
	else:
		userCorrectGuesses = None
	for puzzle in Puzzles.objects.filter(releaseStatus__lte = releaseStage(RELEASE_TIMES)):
		if IsMetaPart1(puzzle):
			continue

		thisPuzzleCorrect = userCorrectGuesses.filter(puzzle=puzzle) if userCorrectGuesses else None

		if thisPuzzleCorrect:
			correctGuess = thisPuzzleCorrect[0]
			puzzleList.append( (puzzle, True, puzzle.solveCount, puzzle.guessCount, correctGuess.pointsAwarded) )
		else:
			puzzleList.append((puzzle, False, puzzle.solveCount, puzzle.guessCount, calcWorth(puzzle, RELEASE_TIMES)))
			
	puzzleList = sorted(puzzleList, key=lambda x:(x[0].act, x[0].scene))

	nextRelease = calcNextRelease(RELEASE_TIMES)
	print(nextRelease)

	return render(request, 'PHapp/puzzles.html', {'puzzleList':puzzleList, 'nextRelease':nextRelease})


def puzzleInfo(request, act, scene):
	if act == 7:
		actNumber = act
	else:
		actNumber = RomanToInt(act)
		if not actNumber:
			raise Http404()
	try:
		puzzle = Puzzles.objects.get(act=actNumber,scene=scene)
	except:
		raise Http404()
	if releaseStage(RELEASE_TIMES) < puzzle.releaseStatus:
		raise Http404()

	allSolves = sorted([[guess, calcSingleTime(guess, RELEASE_TIMES)] for guess in SubmittedGuesses.objects.filter(correct=True, puzzle=puzzle)], key=lambda x:x[1])
	if allSolves:
		avgTime = allSolves[0][1]
		for guess, time in allSolves[1:]:
			avgTime += guess
		avgTime /= len(allSolves)
		averageTimeString = prettyPrintDateTime(avgTime)
	else:
		averageTimeString = '-'
	for i in range(len(allSolves)):
		allSolves[i][1] = prettyPrintDateTime(allSolves[i][1])
	
	totalRight = puzzle.solveCount
	totalWrong = puzzle.guessCount

	return render(request, 'PHapp/puzzleStats.html', 
		{'puzzle':puzzle, 'allSolves':allSolves, 'totalWrong':totalWrong, 'totalRight':totalRight, 'avTime':averageTimeString})

def puzzleInfoMiniMeta(request, act):
	return puzzleInfo(request, act, 5)

def puzzleInfoMeta(request):
	return puzzleInfo(request, 7, 2)

def showPrologue(request):
    return FileResponse(open(os.path.join(settings.BASE_DIR, 'PHapp/puzzleFiles/Prologue.pdf'), 'rb'), content_type='application/pdf')

def showPuzzle(request, act, scene, puzzleName):
	if act == 7:
		actNumber = 7
	else:
		actNumber = RomanToInt(act)
		if not actNumber:
			raise Http404()
	try:
		puzzle = Puzzles.objects.get(act=actNumber,scene=scene)
	except:
		raise Http404()
	if releaseStage(RELEASE_TIMES) < puzzle.releaseStatus:
		raise Http404()
	if puzzleName != puzzle.title and not IsMeta(puzzle):
		if IsMetaOrMiniMeta(puzzle):
			return redirect(showPuzzleMiniMeta, act=act, puzzleName=puzzle.title, permanent=True)
		else:
			return redirect(showPuzzle, act=act, scene=scene, puzzleName=puzzle.title, permanent=True)
	try:
		return FileResponse(open(os.path.join(settings.BASE_DIR, 'PHapp/puzzleFiles/', puzzle.pdfPath + '.pdf'), 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404("PDF file not found!")

def showPuzzleMiniMeta(request, act, puzzleName):
	return showPuzzle(request, act, 5, puzzleName)

def showPuzzleMeta(request):
	return showPuzzle(request, 7, 2, '')

def noGuessesLeft(request, team):
	# Login implicity required. This function only works if the hunt is not over!
	nextGuess = calcNextGuess(RELEASE_TIMES)
	return render(request, 'PHapp/noGuesses.html', {'huntStage': nextGuess[0], 'nextGuesses': nextGuess[1]})

@login_required
def solveMeta(request):
	huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
	if huntOver:
		return render(request, 'PHapp/huntOver.html')
	meta1 = Puzzles.objects.get(act=7, scene=1)
	meta2 = Puzzles.objects.get(act=7, scene=2)
	if releaseStage(RELEASE_TIMES) < meta1.releaseStatus:
		raise Http404()
	
	team = Teams.objects.get(authClone = request.user)
	meta2Guesses = SubmittedGuesses.objects.filter(team=request.user,puzzle=meta2)
	correctGuesses = meta2Guesses.filter(correct=True)
	if correctGuesses:
		correctMeta2Answers = [meta2.answer] + list(AltAnswers.objects.filter(puzzle=meta2))
		correctFinalGuesses = correctGuesses.filter(guess__in=correctMeta2Answers)
		if correctFinalGuesses:
			points = correctFinalGuesses[0].pointsAwarded
			altAns = correctFinalGuesses[0].guess if correctFinalGuesses[0].guess != meta2.answer else None
			return render(request, 'PHapp/solveCorrect.html', {'puzzle':meta2, 'points':points, 'team':team, 'altAns': altAns})
	
	if not team.guesses:
		return noGuessesLeft(request, team)

	solveType = -1
	displayGuess = None
	altAns = None

	if request.method == 'POST':
		solveForm = SolveForm(request.POST)
		if solveForm.is_valid():
			guess = stripToLetters(solveform.cleaned_data['guess'])
			alreadySeen = correctGuesses.filter(guess=guess)
			if alreadySeen:
				# Seen it before, but it's only Meta part 1 (if it were Meta 2 it would have been caught above)
				alreadySeenCorrect = alreadySeen.filter(correct=True)
				if alreadySeenCorrect:
					solveType = SOLVE_METAHALFDUPLICATE
					# Check for alternate answers
					altAns = alreadySeenCorrect[0].guess if alreadySeenCorrect[0].guess != meta1.answer else None
				else:
					solveType = SOLVE_DUPLICATE
				displayGuess = guess
			elif guess == meta1.answer or AltAnswers.objects.filter(puzzle=meta1).filter(altAnswer=guess):
				# This is a Meta 1 answer
				SubmittedGuesses.objects.create(
					team = request.user,
					puzzle = meta1,
					guess = guess,
					correct = True,
					pointsAwarded = calcWorth(meta1, RELEASE_TIMES)
				)
				team.teamPoints += calcWorth(meta1, RELEASE_TIMES)
				team.save()

				solveType = SOLVE_METAHALF
				altAns = guess if guess != meta1.answer else None
			elif guess == meta2.answer or AltAnswers.objects.filter(puzzle=meta2,altAnswer=guess):
				# This is a meta 2 answer
				SubmittedGuesses.objects.create(
					team = request.user,
					puzzle = meta2,
					guess = guess,
					correct = True,
					pointsAwarded = calcWorth(meta2, RELEASE_TIMES)
				)

				solveTime = calcSolveTime(team, RELEASE_TIMES)
				team.avHr = solveTime[1]
				team.avMin = solveTime[2]
				team.avSec = solveTime[3]
				team.teamPoints += calcWorth(meta2, RELEASE_TIMES)
				team.teamPuzzles += 1
				team.save()

				meta2.solveCount = meta2.solveCount + 1
				meta2.save()

				return redirect(f'/solve/meta')
			else:
				solveType = SOLVE_WRONG
				displayGuess = guess
				meta2.guessCount = meta2.guessCount + 1
				meta2.save()
	
	solveForm = SolveForm()
	previousGuesses = SubmittedGuesses.objects.filter(puzzle=puzzle, team=request.user, correct=False).values_list('guess', flat=True)
	# I feel like reverse chronological order of guess submission is more intuitive?
	# previousGuesses = sorted(previousGuesses)
	previousGuesses = previousGuesses[::-1]

	return render(request, 'PHapp/solve.html', 
		{'solveform':solveform, 'solveType': solveType, 'displayGuess':displayGuess, 'puzzle':puzzle, 'team':team, 'previousGuesses':previousGuesses, 'altAns': altAns})

@login_required
def solve(request, act, scene):
	# sanity check; we're not dealing with the Meta
	actNumber = RomanToInt(act)
	if not actNumber:
		raise Http404()
	try:
		puzzle = Puzzles.objects.get(act=actNumber,scene=scene)
	except:
		raise Http404()
	if releaseStage(RELEASE_TIMES) < puzzle.releaseStatus:
		raise Http404()
	
	huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
	if huntOver:
		return render(request, 'PHapp/huntOver.html')

	team = Teams.objects.get(authClone = request.user)
	guesses = SubmittedGuesses.objects.filter(team = request.user, puzzle = puzzle)
	correctGuessList = guesses.filter(correct=True)
	if correctGuessList:
		correctGuess = correctGuessList[0]
		points = correctGuess.pointsAwarded
		altAns = correctGuess.guess if correctGuess.guess != puzzle.answer else None
		return render(request, 'PHapp/solveCorrect.html', {'puzzle':puzzle, 'points':points, 'team':team, 'altAns':altAns})

	if not team.guesses:
		return noGuessesLeft(request, team)

	# Default value
	solveType = -1
	displayGuess = None

	if request.method == 'POST':
		solveform = SolveForm(request.POST)
		if solveform.is_valid():
			guess = stripToLetters(solveform.cleaned_data['guess'])

			if guess == puzzle.answer or AltAnswers.objects.filter(puzzle=puzzle).filter(altAnswer=guess):
				# Correct guess!
				pointsAwarded = calcWorth(puzzle, RELEASE_TIMES)
				SubmittedGuesses.objects.create(
					team = request.user,
					puzzle = puzzle,
					guess = guess,
					correct = True,
					pointsAwarded = pointsAwarded,
				)

				solveTime = calcSolveTime(team, RELEASE_TIMES)
				team.avHr = solveTime[1]
				team.avMin = solveTime[2]
				team.avSec = solveTime[3]
				team.teamPoints += pointsAwarded
				team.teamPuzzles += 1
				team.save()
				puzzle.solveCount = puzzle.solveCount + 1
				puzzle.save()

				try:
			    	webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
					webhookTitle = '**{}** solved **{}.{} {}**'.format(team.teamName, puzzle.act, puzzle.scene, puzzle.title)
					webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
					webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=47872)
					webhook.add_embed(webhookEmbed)
					webhook.execute()
				except:
					pass

				return redirect(f'/solve/{act}/{scene}')

			elif SubmittedGuesses.objects.filter(guess=guess, puzzle=puzzle, team=request.user):
				# Duplicate guess
				solveType = SOLVE_DUPLICATE
				displayGuess = guess

			else:
				# Incorrect guess
				SubmittedGuesses.objects.create(
					team = request.user,
					puzzle = puzzle,
					guess = guess,
					correct = False,
					pointsAwarded = calcWorth(puzzle, RELEASE_TIMES),
				)
				team.guesses -= 1
				team.save()
				solveType = SOLVE_WRONG
				displayGuess = None

				puzzle.guessCount = puzzle.guessCount + 1
				puzzle.save()

				try:
					webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
					webhookTitle = '**{}** incorrectly attempted **{}.{} {}**'.format(team.teamName, puzzle.act, puzzle.scene, puzzle.title)
					webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
					webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=12255232)
					webhook.add_embed(webhookEmbed)
					webhook.execute()
				except:
					pass

	# Reset solve form
	solveform = SolveForm()

	previousGuesses = SubmittedGuesses.objects.filter(puzzle=puzzle, team=request.user, correct=False).values_list('guess', flat=True)
	# I feel like reverse chronological order of guess submission is more intuitive?
	# previousGuesses = sorted(previousGuesses)
	previousGuesses = previousGuesses[::-1]

	return render(request, 'PHapp/solve.html', 
		{'solveform':solveform, 'solveType': solveType, 'displayGuess':displayGuess, 'puzzle':puzzle, 'team':team, 'previousGuesses':previousGuesses})

@login_required
def solveMiniMeta(request, act):
	# Just prettifies the URLs a bit
	return solve(request, act, 5)

def teams(request):
	if not Teams.objects.all():
		return render(request, 'PHapp/teams.html', {'teamsExist':False})

	allTeams = []
	totRank = 1
	ausRank = 1

	for team in Teams.objects.all():
		if team.teamPuzzles:
			allTeams.append([team, "{:02d}h {:02d}m {:02d}s".format(team.avHr, team.avMin, team.avSec), team.avHr, team.avMin, team.avSec])
		else:
			allTeams.append([team, '-', 0, 0, 0])

	# Sort by points, then # of puzzles solved, then average solve time, then ID
	allTeams = sorted(allTeams, key=lambda x:(-x[0].teamPoints, -x[0].teamPuzzles, 3600*x[2]+60*x[3]+x[4], x[0].id) )

	for i in range(len(allTeams)):
		if allTeams[i][0].teamPuzzles:
			allTeams[i].append(i + 1)
			if allTeams[i][0].aussie:
				allTeams[i].append(ausRank)
			else:
				allTeams[i].append('-')
		else:
			allTeams[i] += ['-', '-']
		if allTeams[i][0].aussie:
			ausRank = ausRank + 1

	teamName = None
	if request.user.is_authenticated:
		teamName = request.user.teams.teamName
	
	return render(request, 'PHapp/teams.html', {'allTeams':allTeams, 'teamName':teamName, 'teamsExist':True})

def teamReg(request):
	if request.user.is_authenticated:
		return redirect('/')

	huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
	if huntOver:
		return render(request, 'PHapp/huntOver.html')

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
			
				message = 'Thank you for registering for the 2019 MUMS Puzzle Hunt. Please find below your team details:\n\n' + msg_username + msg_name + 'A reminder that you will need your username, and not your team name, to login.\n\n' + 'Regards,\n' + 'MUMS Puzzle Hunt Organisers'
				subject = '[PH2019] Team registered'
				email_from = settings.EMAIL_HOST_USER
				send_mail( subject, message, email_from, recipient_list )

			
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
	huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
	if huntOver:
		return render(request, 'PHapp/huntOver.html')

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
	try:
		team = Teams.objects.get(id=teamId)
	except:
		raise Http404()
	membersList = sorted(list(Individuals.objects.filter(team=team)), key=lambda x: x.name)
	correctGuesses = SubmittedGuesses.objects.filter(team=team.authClone, correct=True)
	correctList = []
	for guess in correctGuesses:
		if IsMetaPart1(guess.puzzle):
			continue
		correctList += [(str(guess.puzzle), guess, prettyPrintDateTime(calcSingleTime(guess, RELEASE_TIMES)), SubmittedGuesses.objects.filter(team=team.authClone, correct=False, puzzle=guess.puzzle).count())]
	correctList.sort(key=lambda x:x[1].submitTime)
	anySolves = bool(correctList)
	avSolveTime = "{:02d}h {:02d}m {:02d}s".format(team.avHr, team.avMin, team.avSec) if anySolves else '-'
	return render(request, 'PHapp/teamInfo.html', {'team':team, 'members':membersList, 'donation':str(len(membersList)*2),'correctList':correctList, 'anySolves':anySolves, 'avSolveTime':avSolveTime})

def hints(request, act, scene):
	if act == 7:
		actNumber = 7
	else:
		actNumber = RomanToInt(act)
		if not actNumber:
			raise Http404()
	try:
		puzzle = Puzzles.objects.get(act=actNumber,scene=scene)
	except:
		raise Http404()
	if releaseStage(RELEASE_TIMES) < puzzle.releaseStatus:
		raise Http404()

	toRender = []
	anyHints = False
	nextHint = RELEASE_TIMES[puzzle.releaseStatus]
	if releaseStage(RELEASE_TIMES) - puzzle.releaseStatus >= 1:
		toRender.append([1, puzzle.hint1])
		anyHints = True
		nextHint = RELEASE_TIMES[puzzle.releaseStatus + 1]
	if releaseStage(RELEASE_TIMES) - puzzle.releaseStatus >= 2:
		toRender.append([2, puzzle.hint2])
		nextHint = RELEASE_TIMES[puzzle.releaseStatus + 2]
	if releaseStage(RELEASE_TIMES) - puzzle.releaseStatus >= 3:
		toRender.append([3, puzzle.hint3])
		nextHint = None
	return render(request, 'PHapp/hints.html', {'toRender':toRender, 'anyHints':anyHints, 'nextHint':nextHint, 'puzzle':puzzle})

def hintsMiniMeta(request, act):
	return hints(request, act, 5)

def hintsMeta(request):
	return hints(request, 7, 2)

def faq(request):
	return render(request, 'PHapp/faq.html')

def rules(request):
	return render(request, 'PHapp/rules.html')

def debrief(request):
	if not huntFinished(RELEASE_TIMES):
		raise Http404()
	else:
		return render(request, 'PHapp/home.html')

def announcements(request):
	return render(request, 'PHapp/announcements.html')

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