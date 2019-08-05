import datetime
import pytz
from .models import Puzzles, Teams, SubmittedGuesses, Individuals
from .globals import *
import random
import string

def prettyPrintDateTime(td):
	if td.days:
		return f'{td.days}d {td.seconds // 3600}h {(td.seconds // 60) % 60}m {td.seconds % 60}s'
	else:
		return f'{td.seconds // 3600}h {(td.seconds // 60) % 60}m {td.seconds % 60}s'

def stripToLetters(inputStr):
	outputStr = ''.join(char for char in inputStr if char.isalpha())
	return outputStr.upper()

def releaseStage(timeList):
	x = 0
	nowTime = AEST.localize(datetime.datetime.now())
	for i in timeList:
		if nowTime > i:
			x += 1
	return x

def calcWorth(puzzle, timeList):
	if IsMetaPart1(puzzle):
		return 0
	elif IsMeta(puzzle):
		# TODO: Score for meta??
		return 0
	scoreToAddRaw = 5-(releaseStage(timeList) - puzzle.releaseStatus)
	scoreToAdd = scoreToAddRaw if scoreToAddRaw >= 2 else 2
	return scoreToAdd

def checkListAllNone(aList):
	for i in aList:
		if i != None:
			return False
	return True

def totalSolves(team):
	solves = SubmittedGuesses.objects.filter(team=team.authClone, correct=True, puzzle__metaPart1=False).count()
	return solves

def calcSolveTime(team, releaseTimes):
	puzzlesSolved = SubmittedGuesses.objects.filter(team=team.authClone, correct=True, puzzle__metaPart1 = False)
	solves = puzzlesSolved.count()
	if solves == 0:
		return ['-', None, None, None]

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

def calcSingleTime(guess, releaseTimes):
	start = releaseTimes[guess.puzzle.releaseStatus-1]
	solveTime = guess.submitTime - start
	return solveTime

def huntFinished(releaseTimes):
	now = AEST.localize(datetime.datetime.now())
	if now > releaseTimes[-1]:
		return True
	else:
		return False

def calcNextRelease(releaseTimes):
	now = AEST.localize(datetime.datetime.now())

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

def calcNextGuess(releaseTimes):
	'''
		Returns a tuple (SITUATION, time to next guess release)
		Possible values of SITUATION:
		0: Puzzle hunt is yet to start
		1: Puzzle hunt is underway; next guesses will be released at time specified
		2: Puzzle hunt is underway; no more guesses will be released
		3: Puzzle hunt is over
	'''
	# TODO: handle end of hunt properly
	now = AEST.localize(datetime.datetime.now())

	if now < releaseTimes[0]:
		return (0, prettyPrintDateTime(releaseTimes[0] - now))
	else:
		for time in releaseTimes[1:]:
			if time > now:
				return (1, prettyPrintDateTime(time - now))
	return (2, None)

def cubeTestRelease(releaseTimes):
	stage = releaseStage(releaseTimes)
	textMap = [
	['1', '3', '', '', '4',''], # 0
	['', '', '', '', '', ''], # 1
	['2', '4', '1', '', '', ''], # 2
	['', '', '', '', '', ''], # 3
	['I.', '', '', '', '', ''], # 4
	['', '', '', '', '', ''], # 5
	['3', '', '', '3', '3', ''], # 6
	['', '', '', '', '', ''], # 7
	['4', '', '3', '1', '', ''], # 8
	['', '', '', '', '', ''], # 9
	['', 'II.', '', '', '', ''], # 10
	['', '', '', '', '', ''], # 11
	['', '', '', '', 'V.', ''], # 12
	['', '', '', '', '', ''], # 13
	['', '', 'III.', '', '', ''], # 14
	['', '', '', '', '', ''], # 15
	['', '', '', 'IV.', '', ''], # 16
	['', '', '', '', '', ''], # 17
	['', '1', '', '', '2', '4'], # 18
	['', '', '', '', '', ''], # 19
	['', '2', '2', '', '', '2'], # 20
	['', '', '', '', '', ''], # 21
	['', '', '', '', '', 'VI.'], # 22
	['', '', '', '', '', ''], # 23
	['', '', '', '4', '1', '3'], # 24
	['', '', '', '', '', ''], # 25
	['', '', '4', '2', '', '1']] # 26
	if stage >= 6:
		return textMap

	for i in range(len(textMap)):
		for j in range(stage, 6):
			textMap[i][j] = ''

	return textMap

def IsMeta(puzzle):
	return (puzzle.act == 7)

def IsMetaPart1(puzzle):
	return (puzzle.act == 7 and puzzle.scene == 1)

def IsMetaOrMiniMeta(puzzle):
	return (IsMeta(puzzle) or puzzle.scene == 5)

def cubeDataColourCell(puzzle):
	if IsMeta(puzzle):
		return None
	return CUBE_CELL_MAP[puzzle.act][puzzle.scene]

def cubeDataColourCellCoords(act, scene):
    return CUBE_CELL_MAP[act][scene]

def RomanToInt(roman):
	roman = str(roman)
	if roman in ('I', 'II', 'III', 'IV', 'V', 'VI'):
		return ('I', 'II', 'III', 'IV', 'V', 'VI').index(roman) + 1
	return None

def IntToRoman(i):
	if i < 1 or i > 6:
		return 0
	else:
		 return ('I', 'II', 'III', 'IV', 'V', 'VI')[i-1]

def generateToken():
	choice = string.ascii_lowercase + string.ascii_uppercase + string.digits
	token = ''
	for i in range(64):
		token += random.choice(choice)
	return token