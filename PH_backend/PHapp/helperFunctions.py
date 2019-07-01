import datetime
import pytz
from .models import Puzzles, Teams, SubmittedGuesses, Individuals

aest = pytz.timezone("Australia/Melbourne")

def stripToLetters(inputStr):
	allAlph = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	outputStr = ''
	for char in inputStr:
		if char in allAlph:
			outputStr += char
	return outputStr.upper()

def releaseStage(timeList):
	aest = pytz.timezone("Australia/Melbourne")
	x = 0
	nowTime = aest.localize(datetime.datetime.now())
	for i in timeList:
		if nowTime > i:
			x += 1
	return x

def calcWorth(puzzle, timeList):
	scoreToAddRaw = 5-(releaseStage(timeList) - puzzle.releaseStatus)
	scoreToAdd = scoreToAddRaw if scoreToAddRaw >= 2 else 2
	return scoreToAdd

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
		return ['-', None, None, None]
	puzzlesSolved = SubmittedGuesses.objects.filter(team=team.authClone, correct=True)

	totalTime = datetime.timedelta(0)
	for guess in puzzlesSolved:
		start = releaseTimes[guess.puzzle.releaseStatus-1]
		solveTime = guess.submitTime - start
		totalTime += solveTime

	x = totalTime/solves
	xh = x.days*24 + x.seconds//3600
	xm = (x.seconds//60)%60
	xs = x.seconds%60
	
	return ["{:02d}h {:02d}m {:02d}s".format(xh, xm, xs), xh, xm, xs]

def calcPuzzleTime(puzzle, releaseTimes):
	solves = SubmittedGuesses.objects.filter(puzzle=puzzle, correct=True)

	if len(solves) == 0:
		return ['-', None, None, None]

	totalTime = datetime.timedelta(0)
	for guess in solves:
		start = releaseTimes[guess.puzzle.releaseStatus-1]
		solveTime = guess.submitTime - start
		totalTime += solveTime

	x = totalTime/len(solves)
	xh = x.days*24 + x.seconds//3600
	xm = (x.seconds//60)%60
	xs = x.seconds%60
	
	return ["{:02d}h {:02d}m {:02d}s".format(xh, xm, xs), xh, xm, xs]

def calcSingleTime(guess, submitTime, releaseTimes):
	start = releaseTimes[guess.puzzle.releaseStatus-1]
	solveTime = submitTime - start
	xh = solveTime.days*24 + solveTime.seconds//3600
	xm = (solveTime.seconds//60)%60
	xs = solveTime.seconds%60

	return ["{:02d}h {:02d}m {:02d}s".format(xh, xm, xs), xh, xm, xs]

def huntFinished(releaseTimes):
	aest = pytz.timezone("Australia/Melbourne")
	now = aest.localize(datetime.datetime.now())
	if (now-releaseTimes[-1]).days >= 0:
		return True
	else:
		return False

def calcNextRelease(releaseTimes):
	aest = pytz.timezone("Australia/Melbourne")
	now = aest.localize(datetime.datetime.now())

	for i in range(len(releaseTimes)):
		if (releaseTimes[i]-now).days >= 0:
			days = (releaseTimes[i]-now).days
			hrs = (releaseTimes[i]-now).seconds//3600
			mins = ((releaseTimes[i]-now).seconds//60)%60
			secs = (releaseTimes[i]-now).seconds%60
			
			if i == 0:
				return [0,"{:02d}d {:02d}h {:02d}m {:02d}s".format(days,hrs,mins,secs),days,hrs,mins,secs]
			elif i-len(releaseTimes) ==  - 1:
				return [3,"{:02d}d {:02d}h {:02d}m {:02d}s".format(days,hrs,mins,secs),days,hrs,mins,secs]
			elif -4 <= i-len(releaseTimes) < -1:
				return [2,"{:02d}d {:02d}h {:02d}m {:02d}s".format(days,hrs,mins,secs),days,hrs,mins,secs]
			elif i-len(releaseTimes) < -4:
				return [1,"{:02d}d {:02d}h {:02d}m {:02d}s".format(days,hrs,mins,secs),days,hrs,mins,secs]

	return [4,None,None,None,None,None]