import datetime
from .models import Puzzles, Teams, SubmittedGuesses, Individuals

def stripToLetters(inputStr):
	allAlph = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	outputStr = ''
	for char in inputStr:
		if char in allAlph:
			outputStr += char
	return outputStr.upper()

def releaseStage(timeList):
	x = 0
	nowTime = datetime.datetime.now()
	for i in timeList:
		if nowTime > i:
			x += 1
	return x

def checkListAllNone(aList):
	for i in aList:
		if i != None:
			return False
	return True

def totalSolves(team):
	solves = len(SubmittedGuesses.objects.filter(team=team.authClone, correct=True))
	return solves

def calcSolveTime(team, releaseTimes):
	solves = totalSolves(team)
	if solves == 0:
		return checkListAllNone
	puzzlesSolved = SubmittedGuesses.objects.filter(team=team.authClone, correct=True)

	totalTime = datetime.timedelta(0)
	for guess in puzzlesSolved:
		start = releaseTimes[guess.puzzle.releaseStatus-1]
		solveTime = datetime.datetime.now() - start
		totalTime += solveTime

	return totalTime/solves