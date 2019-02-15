from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth.models import User
from .models import Puzzles, Teams, SubmittedGuesses
from .forms import SolveForm, TeamRegForm, IndividualRegForm
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
	puzzleList = [i for i in Puzzles.objects.exclude(releaseStatus = -1)]
	puzzleList = sorted(puzzleList, key=lambda x:x.act*10+x.scene)
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
		regForm = TeamRegForm(request.POST)
		if regForm.is_valid():
			pass
	else:
		regForm = TeamRegForm()
		memberForms = {i+1:IndividualRegForm() for i in range(10)}
	return render(request, 'PHapp/teamReg.html', {'regForm':regForm, 'memberForms':memberForms})

def faq(request):
	return render(request, 'PHapp/faq.html')

def teams(request):
	return render(request, 'PHapp/home.html')