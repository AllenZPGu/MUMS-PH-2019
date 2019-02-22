from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth.models import User
from django.forms import formset_factory, ValidationError
from .models import Puzzles, Teams, SubmittedGuesses, Individuals, CorrectGuesses
from .forms import SolveForm, TeamRegForm, IndivRegForm, IndivRegFormSet, LoginForm
from django.conf import settings
import json
import datetime
import random
import os
from .helperFunctions import *

def index(request):
	return render(request, 'PHapp/home.html')

@login_required
def puzzles(request):
	puzzleList = []
	for puzzle in Puzzles.objects.exclude(releaseStatus = -1):
		allGuesses = [i.correct for i in SubmittedGuesses.objects.filter(puzzle=puzzle)]
		if len(CorrectGuesses.objects.filter(puzzle=puzzle, team=request.user)) == 0:
			puzzleList.append([puzzle, False, sum(allGuesses), len(allGuesses)])
		else:
			puzzleList.append([puzzle, True, sum(allGuesses), len(allGuesses)])
	puzzleList = sorted(puzzleList, key=lambda x:x[0].id)
	return render(request, 'PHapp/puzzles.html', {'puzzleList':puzzleList})

@login_required
def showPuzzle(request, puzzleURL):
	try:
		return FileResponse(open(os.path.join(settings.BASE_DIR, 'PHapp/puzzleFiles/', puzzleURL), 'rb'), content_type='application/pdf')
	except FileNotFoundError:
		raise Http404("PDF file not found at "+os.path.join(settings.BASE_DIR, 'PHapp/puzzleFiles/', puzzleURL))

@login_required
def solve(request, chapter, status):
	if status not in ('solve', 'wrong'):
		raise Http404("This site does not exist!!!!!")

	puzzle = Puzzles.objects.get(act = chapter[0], scene = chapter[2])
	
	if True in [i.correct for i in SubmittedGuesses.objects.filter(team = request.user, puzzle = puzzle)]:
		return render(request, 'PHapp/solveCorrect.html', {'puzzle':puzzle})
	
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

				newCorrectGuess = CorrectGuesses()
				newCorrectGuess.team = request.user
				newCorrectGuess.puzzle = puzzle
				newCorrectGuess.subGuessKey = newSubmit
				newCorrectGuess.save()

				return redirect('/solve/{}/solve'.format(chapter))
			else:
				newSubmit.correct = False
				newSubmit.save()
				return redirect('/solve/{}/wrong'.format(chapter))
	else:
		solveform = SolveForm()

	return render(request, 'PHapp/solve.html', {'solveform':solveform, 'chapter':chapter, 'status':status, 'puzzle':puzzle})

def teamReg(request):
	if request.user.is_authenticated:
		raise Http404("Your team has already been registered.")

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

def faq(request):
	return render(request, 'PHapp/faq.html')

def teams(request):
	allTeams = Teams.objects.all()
	allTeams = sorted(allTeams, key=lambda x:-x.teamPoints)
	return render(request, 'PHapp/teams.html', {'allTeams':allTeams})

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