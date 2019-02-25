from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth.models import User
from django.forms import formset_factory, ValidationError
from .models import Puzzles, Teams, SubmittedGuesses, Individuals
from .forms import SolveForm, TeamRegForm, IndivRegForm, IndivRegFormSet, LoginForm
from django.conf import settings
import json
import datetime
import random
import os
from .helperFunctions import *

#releaseTimes = [datetime.datetime(2019, 4, 24, 12) + datetime.timedelta(days=i) for i in range(10)]
releaseTimes = [datetime.datetime(2019, 2, 22, 12) + datetime.timedelta(days=i) for i in range(10)]

def index(request):
	return render(request, 'PHapp/home.html')

@login_required
def puzzles(request):
	puzzleList = []
	for puzzle in Puzzles.objects.filter(releaseStatus__lte = releaseStage(releaseTimes)):
		allGuesses = [i.correct for i in SubmittedGuesses.objects.filter(puzzle=puzzle)]
		if len(SubmittedGuesses.objects.filter(puzzle=puzzle, team=request.user, correct=True)) == 0:
			puzzleList.append([puzzle, False, sum(allGuesses), len(allGuesses)-sum(allGuesses)])
		else:
			puzzleList.append([puzzle, True, sum(allGuesses), len(allGuesses)-sum(allGuesses)])
	puzzleList = sorted(puzzleList, key=lambda x:x[0].id)
	return render(request, 'PHapp/puzzles.html', {'puzzleList':puzzleList})

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
	
	if True in [i.correct for i in SubmittedGuesses.objects.filter(team = request.user, puzzle = puzzle)]:
		return render(request, 'PHapp/solveCorrect.html', {'puzzle':puzzle})

	team = Teams.objects.get(authClone = request.user)

	if team.guesses <= 0:
		return render(request, 'PHapp/noGuesses.html')
	
	if request.method == 'POST':
		solveform = SolveForm(request.POST)
		if solveform.is_valid():
			guess = stripToLetters(solveform.cleaned_data['guess'])
			newSubmit = SubmittedGuesses()
			newSubmit.team = request.user
			newSubmit.puzzle = puzzle
			newSubmit.guess = guess
			newSubmit.submitTime = datetime.datetime.now()
			if guess == puzzle.answer:
				newSubmit.correct = True
				newSubmit.save()
				return render(request, 'PHapp/solveCorrect.html', {'puzzle':puzzle})
			else:
				newSubmit.correct = False
				newSubmit.save()
				team.guesses -= 1
				team.save()
				displayWrong = True
	else:
		solveform = SolveForm()
		displayWrong = False

	return render(request, 'PHapp/solve.html', 
		{'solveform':solveform, 'displayWrong':displayWrong, 'puzzle':puzzle})

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

			newTeam.save()
			return redirect('/')
	
	else:
		userForm = UserCreationForm()
		regForm = TeamRegForm()
		indivFormSet = IndivRegFormSet()
	return render(request, 'PHapp/teamReg.html', {'userForm':userForm, 'regForm':regForm, 'indivFormSet':indivFormSet})

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
	return render(request, 'PHapp/hints.html', {'toRender':toRender, 'anyHints':anyHints, 'nextHint':nextHint})

@login_required
def stats(request, title):
	try:
		puzzle = Puzzles.objects.get(pdfPath=title)
	except:
		raise Http404()
	if releaseStage(releaseTimes) < puzzle.releaseStatus:
		raise Http404()

	allGuesses = SubmittedGuesses.objects.filter(puzzle=puzzle)
	allSolves = sorted([i for i in allGuesses if i.correct], key=lambda x:x.submitTime)
	
	totalRight = len(allSolves)
	totalWrong = len(allGuesses) - totalRight

	return render(request, 'PHapp/puzzleStats.html', {'puzzle':puzzle, 'allSolves':allSolves, 'totalWrong':totalWrong, 'totalRight':totalRight})

def faq(request):
	return render(request, 'PHapp/faq.html')

def teams(request):
	allTeamsRaw = Teams.objects.all()
	allTeams = []
	for i in range(len(allTeamsRaw)):
		solves = len(SubmittedGuesses.objects.filter(team=allTeamsRaw[i].authClone, correct=True))
		allTeams.append([1, 1, allTeamsRaw[i], solves, calcSolveTime(allTeamsRaw[i], releaseTimes)])
	print(allTeams)
	teamName = None
	if request.user.is_authenticated:
		teamName = Teams.objects.get(authClone = request.user).teamName
	return render(request, 'PHapp/teams.html', {'allTeams':allTeams, 'teamName':teamName})

def teamInfo(request, teamId):
	team = Teams.objects.get(id=teamId)
	membersList = Individuals.objects.filter(team=team)
	correctList = [[i, 0, 0] for i in SubmittedGuesses.objects.filter(team=team.authClone, correct=True)]
	correctList = sorted(correctList, key=lambda x:x[0].submitTime)
	anySolves = True if len(correctList) > 0 else False
	return render(request, 'PHapp/teamInfo.html', {'team':team, 'members':membersList, 'correctList':correctList, 'anySolves':anySolves})

def about(request):
	return render(request, 'PHapp/about.html')

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