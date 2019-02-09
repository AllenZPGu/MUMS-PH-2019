from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth.models import User
from .models import Puzzles, Teams, SubmittedGuesses
from .forms import SolveForm
from django.conf import settings
import json
import datetime
import random

def stripToLetters(inputStr):
	allAlph = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	outputStr = ''
	for char in inputStr:
		if char in allAlph:
			outputStr += char
	return outputStr.lower()

def index(request):
	return render(request, 'PHapp/home.html')

@login_required
def puzzles(request):
	puzzleList = [i for i in Puzzles.objects.exclude(releaseStatus = -1)]
	puzzleList = sorted(puzzleList, key=lambda x:x.act*10+x.scene)
	return render(request, 'PHapp/puzzles.html', {'puzzleList':puzzleList})

@login_required
def solve(request, chapter, status):
	if status not in ('solve', 'wrong'):
		raise Http404("This site does not exist!!!!!")

	puzzle = Puzzles.objects.get(act = chapter[0], scene = chapter[2])
	
	if True in [i.correct for i in SubmittedGuesses.objects.filter(team = request.user)]:
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
				return redirect('/solve/{}/solve'.format(chapter))
			else:
				newSubmit.correct = False
				newSubmit.save()
				return redirect('/solve/{}/wrong'.format(chapter))
	else:
		solveform = SolveForm()

	return render(request, 'PHapp/solve.html', {'solveform':solveform, 'chapter':chapter, 'status':status, 'puzzle':puzzle})

def faq(request):
	return render(request, 'PHapp/faq.html')

def teams(request):
	return render(request, 'PHapp/home.html')