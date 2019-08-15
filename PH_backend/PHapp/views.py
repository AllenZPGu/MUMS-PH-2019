from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.contrib.auth.models import User
from django.forms import formset_factory, ValidationError
from django.core import mail
from django.core.mail import send_mail
from django.views.decorators.http import last_modified
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import *
from .forms import *
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

SOLVE_WRONG = 0
SOLVE_DUPLICATE = 1
SOLVE_METAHALF = 2
SOLVE_METAHALFDUPLICATE = 3
SOLVE_EMPTYSTRING = 4
SOLVE_METAALT = 5

turnOnDiscord = True

#releaseTimes = [aest.localize(datetime.datetime(2019, 6, 24, 12)) + datetime.timedelta(days=i) for i in range(10)]
@never_cache
def index(request):
    huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
    return render(request, 'PHapp/home.html', {'huntOver':huntOver})

@never_cache
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
@never_cache
def cubeData(request):
    huntOver = (releaseStage(RELEASE_TIMES) > len(RELEASE_TIMES))
    if huntOver:
        responseData = [{'colors': [color for color in PUZZLE_COLOURS[i]], 'text': ['']*6, 'links': ['']*6} for i in range(27)]
    else:
        responseData = [{'colors': [color for color in PUZZLE_COLOURS_BLANK[i]], 'text': ['']*6, 'links': ['']*6} for i in range(27)]
    if not huntOver and request.user.is_authenticated:
#        CubeDataAccessRecord.objects.create(user = request.user)
        correctGuesses = SubmittedGuesses.objects.filter(team=request.user, correct=True).select_related('puzzle')

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
            for i in range(1, 7):
                if metascomplete[i]:
                    for j in range(5,10):
                        colourcell = cubeDataColourCellCoords(i, j)
                        responseData[colourcell[0]]['colors'][colourcell[1]] = PUZZLE_COLOURS[colourcell[0]][colourcell[1]]
    availablePuzzles = Puzzles.objects.filter(releaseStatus__lte = releaseStage(RELEASE_TIMES))
    for puzzle in availablePuzzles:
        if not IsMeta(puzzle):
            colourcell = cubeDataColourCell(puzzle)
            responseData[colourcell[0]]['links'][colourcell[1]] = reverse(showPuzzle, kwargs={'act': IntToRoman(puzzle.act), 'scene': puzzle.scene, 'puzzleName': puzzle.title})
            responseData[colourcell[0]]['text'][colourcell[1]] = PUZZLE_TEXTS[colourcell[0]][colourcell[1]]

    return HttpResponse('window.rawcubedata=' + json.dumps(responseData,separators=(',', ':')), content_type='application/javascript')

def puzzles(request):
    puzzleList = []
    isGB = False
    if request.user.is_authenticated:
        userCorrectGuesses = SubmittedGuesses.objects.filter(correct=True, team=request.user)
        if request.user.id == 1:
            isGB = True
    else:
        userCorrectGuesses = None
    for puzzle in Puzzles.objects.filter(releaseStatus__lte = releaseStage(RELEASE_TIMES)):
        if IsMetaPart1(puzzle):
            continue

        thisPuzzleCorrect = userCorrectGuesses.filter(puzzle=puzzle) if userCorrectGuesses else None

        if thisPuzzleCorrect:
            correctGuess = thisPuzzleCorrect[0]
            puzzleList.append((True, puzzle, True, puzzle.solveCount, puzzle.guessCount, correctGuess.pointsAwarded) )
        else:
            puzzleList.append((True, puzzle, False, puzzle.solveCount, puzzle.guessCount, calcWorth(puzzle, RELEASE_TIMES)))
            
    puzzleList = sorted(puzzleList, key=lambda x:(x[1].act, x[1].scene))

    #adding gaps in table
    realPuzzleList = []
    n = 0
    for i in puzzleList:
        if i[1].act == 7:
            realPuzzleList.append((False, f'Meta', None, None, None, None))
        elif n < i[1].act:
            n = i[1].act
            realPuzzleList.append((False, f'Act {IntToRoman(n)}', None, None, None, None))
        realPuzzleList.append(i)

    nextRelease = calcNextRelease(RELEASE_TIMES)

    messageList = [(i.msg, i.msgTime.astimezone(AEST).strftime("%d/%m/%Y %I:%M%p").lower()) for i in sorted(list(Announcements.objects.filter(erratum=True)), key=lambda x: x.msgTime)]
    messageList.reverse()

    colspan = 6
    colspan = colspan + 1 if isGB else colspan
    colspan = colspan + 1 if huntFinished(RELEASE_TIMES) else colspan

    return render(request, 'PHapp/puzzles.html', {'puzzleList':realPuzzleList, 
        'nextRelease':nextRelease, 'isGB':isGB, 'messageList':messageList, 'huntFinished':huntFinished(RELEASE_TIMES), 'colspan':colspan})


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

    userGB = Teams.objects.get(id=1).authClone
    allGuesses = SubmittedGuesses.objects.filter(puzzle=puzzle).exclude(team=userGB)
    allSolves = sorted([[guess, calcSingleTime(guess, RELEASE_TIMES)] for guess in allGuesses.filter(correct=True) ], key=lambda x:x[1])
    if allSolves:
        avgTime = allSolves[0][1]
        for guess, time in allSolves[1:]:
            avgTime += time
        avgTime /= len(allSolves)
        averageTimeString = prettyPrintDateTime(avgTime)
    else:
        averageTimeString = '-'
    for i in range(len(allSolves)):
        allSolves[i][1] = prettyPrintDateTime(allSolves[i][1])
    
    totalRight = puzzle.solveCount
    totalWrong = puzzle.guessCount

    wrongGuessingTeams = [guess.team for guess in allGuesses.filter(correct=False)]
    wGTL = sorted(countInList(wrongGuessingTeams), key=lambda x:-x[1])
    wGTL = [[Teams.objects.get(authClone=i[0]), i[1]] for i in wGTL]

    return render(request, 'PHapp/puzzleStats.html', 
        {'puzzle':puzzle, 'allSolves':allSolves, 'totalWrong':totalWrong, 'totalRight':totalRight, 'avTime':averageTimeString, 'wrongGuesses':wGTL})

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
    GB = Teams.objects.get(id=1)
    meta2Guesses = SubmittedGuesses.objects.filter(team=request.user, puzzle=meta2)
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
    altMessage = None

    if request.method == 'POST':
        solveform = SolveForm(request.POST)
        if solveform.is_valid():
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
                    pointsAwarded = 0
                )
                team.solvedMetaOne = True
                team.save()

                solveType = SOLVE_METAHALF
                altAns = guess if guess != meta1.answer else None

                if turnOnDiscord:
                    try:
                        webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
                        webhookTitle = '**{}** solved the first part of the **META**'.format(team.teamName)
                        webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
                        webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=47872)
                        webhook.add_embed(webhookEmbed)
                        webhook.execute()
                    except:
                        pass


            elif guess == meta2.answer or AltAnswers.objects.filter(puzzle=meta2, altAnswer=guess):
                # This is a meta 2 answer
                SubmittedGuesses.objects.create(
                    team = request.user,
                    puzzle = meta2,
                    guess = guess,
                    correct = True,
                    pointsAwarded = 0
                )

                solveTime = calcSolveTime(team, RELEASE_TIMES)
                team.avHr = solveTime[1]
                team.avMin = solveTime[2]
                team.avSec = solveTime[3]
                team.solvedMetaTwo = True
                team.save()

                if team.id != 1:
                    meta2.solveCount = meta2.solveCount + 1
                meta2.save()
                if turnOnDiscord:
                    try:
                        webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
                        webhookTitle = '**{}** solved **META**'.format(team.teamName)
                        webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
                        webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=47872)
                        webhook.add_embed(webhookEmbed)
                        webhook.execute()
                    except:
                        pass

                return redirect(f'/solve/meta')

            elif IncorrectAnswer.objects.filter(puzzle=meta2, answer=guess):
                x = IncorrectAnswer.objects.filter(puzzle=meta2, answer=guess)[0]
                solveType = SOLVE_METAALT
                displayGuess = guess
                altMessage = (x.title, x.message)

            else:
                solveType = SOLVE_WRONG
                displayGuess = guess
                if team.id != 1:
                    meta2.guessCount = meta2.guessCount + 1
                meta2.save()
                team.guesses -= 1
                team.save()
                SubmittedGuesses.objects.create(
                    team = request.user,
                    puzzle = meta2,
                    guess = guess,
                    correct = False,
                    pointsAwarded = 0
                )

                if turnOnDiscord:
                    try:
                        webhook = DiscordWebhook(url=settings.SOLVE_BOT_URL)
                        webhookTitle = '**{}** incorrectly attempted **META**'.format(team.teamName)
                        webhookDesc = 'Guess: {}\nPoints: {}, Solves: {}'.format(guess, team.teamPoints, team.teamPuzzles)
                        webhookEmbed = DiscordEmbed(title=webhookTitle, description=webhookDesc, color=12255232)
                        webhook.add_embed(webhookEmbed)
                        webhook.execute()
                    except:
                        pass
                
                specialAnswers = IncorrectAnswer.objects.filter(puzzle=meta2, answer=guess)
                if specialAnswers:
                    altMessage = (specialAnswers[0].title, specialAnswers[0].message)

    
    solveform = SolveForm()
    previousGuesses = SubmittedGuesses.objects.filter(puzzle=meta2, team=request.user, correct=False).order_by('-submitTime').values_list('guess', flat=True)
    # I feel like reverse chronological order of guess submission is more intuitive? ## No cause it'll be easier to search for guesses alphabetically   
    # previousGuesses = sorted(previousGuesses)

    return render(request, 'PHapp/solve.html', 
        {'solveform':solveform, 'solveType': solveType, 'displayGuess':displayGuess, 'puzzle':meta2, 'team':team, 'previousGuesses':previousGuesses, 'altAns': altAns, 'altMessage': altMessage})

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
    altMessage = None

    if request.method == 'POST':
        solveform = SolveForm(request.POST)
        if solveform.is_valid():
            guess = stripToLetters(solveform.cleaned_data['guess'])

            specialAnswers = IncorrectAnswer.objects.filter(puzzle=puzzle, answer=guess)

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
                if team.id != 1:
                    puzzle.solveCount = puzzle.solveCount + 1
                puzzle.save()

                if turnOnDiscord:
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

            elif specialAnswers:
                altMessage = (specialAnswers[0].title, specialAnswers[0].message)
                displayGuess = guess
                solveType = SOLVE_WRONG

            elif SubmittedGuesses.objects.filter(guess=guess, puzzle=puzzle, team=request.user):
                # Duplicate guess
                solveType = SOLVE_DUPLICATE
                displayGuess = guess

            elif guess == '':
                solveType = SOLVE_EMPTYSTRING
                displayGuess = False

            else:
                # Incorrect guess
                SubmittedGuesses.objects.create(
                    team = request.user,
                    puzzle = puzzle,
                    guess = guess,
                    correct = False,
                    pointsAwarded = calcWorth(puzzle, RELEASE_TIMES),
                )
                
                solveType = SOLVE_WRONG
                displayGuess = None

                team.guesses -= 1
                team.save()
                if team.id != 1:
                    puzzle.guessCount = puzzle.guessCount + 1
                puzzle.save()

                if turnOnDiscord:
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

    previousGuesses = SubmittedGuesses.objects.filter(puzzle=puzzle, team=request.user, correct=False).order_by('-submitTime').values_list('guess', flat=True)
    # I feel like reverse chronological order of guess submission is more intuitive?
    # previousGuesses = sorted(previousGuesses)

    return render(request, 'PHapp/solve.html', 
        {'solveform':solveform, 'solveType': solveType, 'displayGuess':displayGuess, 'puzzle':puzzle, 'team':team, 'previousGuesses':previousGuesses, 'altMessage': altMessage})

@login_required
def solveMiniMeta(request, act):
    # Just prettifies the URLs a bit
    return solve(request, act, 5)

def guesslog(request, act, scene):
    if request.user.is_authenticated:
        if request.user.username != 'testaccount':
            raise Http404()
    else:
        raise Http404()

    if act == 7:
        actNumber = 7
    else:
        actNumber = RomanToInt(act)
        if not actNumber:
            raise Http404()

    if scene == 'S':
        scene = 5
    else:
        try:
            scene = int(scene)
        except:
            raise Http404()
    
    try:
        puzzle = Puzzles.objects.get(act=actNumber,scene=scene)
        correct = [puzzle.answer] + [i.altAnswer for i in AltAnswers.objects.filter(puzzle=puzzle)]
        if actNumber == 7:
            meta1 = Puzzles.objects.get(act=7,scene=1)
            correct += [meta1.answer] + [i.altAnswer for i in AltAnswers.objects.filter(puzzle=meta1)]
            allGuesses = [i.guess for i in SubmittedGuesses.objects.filter(puzzle__in=(meta1, puzzle)).exclude(team=request.user)]
        else:
            allGuesses = [i.guess for i in SubmittedGuesses.objects.filter(puzzle=puzzle).exclude(team=request.user)]
        counted = countInList(allGuesses)
    except:
        raise Http404()

    counted = sorted(counted, key=lambda x:x[0])
    counted = sorted(counted, key=lambda x:-x[1])

    for i in range(len(counted)):
        if counted[i][0] in correct:
            counted[i] += [True]
        else:
            counted[i] += [False]

    return render(request, 'PHapp/guesslog.html', {'counted':counted, 'puzzle':puzzle})

def guesslogMeta(request):
    return guesslog(request, 7, 2)

def solution(request, act, scene):
    if not huntFinished(RELEASE_TIMES):
        raise Http404()

    if act == 7:
        actNumber = 7
    else:
        actNumber = RomanToInt(act)
        if not actNumber:
            raise Http404()

    if scene == 'S':
        scene = 5
    else:
        try:
            scene = int(scene)
        except:
            raise Http404()

    try:
        puzzle = Puzzles.objects.get(act=actNumber,scene=scene)
    except:
        raise Http404()
    
    return render(request, f'PHapp/solutions/{actNumber}.{scene}.html', {'puzzle':puzzle})

def solutionMeta(request, act, scene):
    if not huntFinished(RELEASE_TIMES):
        raise Http404()

    try:
        puzzle = Puzzles.objects.get(act=7,scene=2)
    except:
        raise Http404()

    return render(request, 'PHapp/solutions/meta.html', {'puzzle':puzzle})


















def teams(request):
    if not Teams.objects.all():
        return render(request, 'PHapp/teams.html', {'teamsExist':False})

    allTeams = []
    totRank = 1
    ausRank = 1

    for team in Teams.objects.exclude(id = 1):
        if team.teamPuzzles:
            allTeams.append([team, "{:02d}h {:02d}m {:02d}s".format(team.avHr, team.avMin, team.avSec), team.avHr, team.avMin, team.avSec])
        else:
            allTeams.append([team, '-', 0, 0, 0])

    # Sort by points, then # of puzzles solved, then average solve time, then ID
    allTeams = sorted(allTeams, key=lambda x:(-x[0].teamPoints, -puzzleSolveCountByTeam(x[0]), 3600*x[2]+60*x[3]+x[4], x[0].id) )

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
                subject = '[MPH 2019] Team registered'
                email_from = settings.EMAIL_HOST_USER
                send_mail( subject, message, email_from, recipient_list )

            
                # message = 'Subject: [MPH 2019] Team registered\n\nThank you for registering for the 2019 MUMS Puzzle Hunt. Please find below your team details:\n\n' + msg_username + msg_name + 'A reminder that you will need your username, and not your team name, to login.\n\n' + 'Regards,\n' + 'MUMS Puzzle Hunt Organisers'
                # context = ssl.create_default_context()
                # with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as emailServer:
                #     emailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                #     emailServer.sendmail(settings.EMAIL_HOST_USER, recipient_list, message)
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

    if team.id == 1:
        if request.user.is_authenticated:
            if request.user.username != 'testaccount':
                raise Http404()
        else:
            raise Http404()


    membersList = sorted(list(Individuals.objects.filter(team=team)), key=lambda x: x.name)
    allGuesses = SubmittedGuesses.objects.filter(team=team.authClone).select_related('puzzle')
    correctGuesses = allGuesses.filter(team=team.authClone, correct=True)
    correctList = []
    for guess in correctGuesses:
        if IsMetaPart1(guess.puzzle):
            continue
        correctList += [(str(guess.puzzle), guess, prettyPrintDateTime(calcSingleTime(guess, RELEASE_TIMES)), allGuesses.filter(correct=False, puzzle=guess.puzzle).count())]
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
    messageList = [(i.msg, i.msgTime.astimezone(AEST).strftime("%d/%m/%Y %I:%M%p").lower()) for i in sorted(list(Announcements.objects.all()), key=lambda x: x.msgTime)]
    messageList.reverse()
    return render(request, 'PHapp/announcements.html', {'messageList':messageList})

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
                try:
                    return redirect(request.GET['next'])
                except:
                    return redirect('/')
    else:
        loginForm = LoginForm()

    return render(request, 'PHapp/login.html', {'loginForm':loginForm, 'wrong':False})

def logoutCustom(request):
    logout(request)
    return redirect('/')

def passwordChange(request):
    if request.method == 'POST':
        emailForm = PasswordChangeEmail(request.POST)
        if emailForm.is_valid():
            email = emailForm.cleaned_data.get('email')
            indivList = list(Individuals.objects.filter(email=email))
            teamList = list(Teams.objects.filter(teamEmail=email))
            if indivList or teamList:
                checkTeamList = [i.team for i in indivList] + teamList

                if all([i == checkTeamList[0] for i in checkTeamList]):
                    team = checkTeamList[0]
                    user = team.authClone
                    token = generateToken()
                    while len(ResetTokens.objects.filter(token=token)) > 0:
                        token = generateToken()
                    ResetTokens.objects.create(
                        token = token,
                        user = user
                    )

                    try:
                        resetLink = f'{settings.WEB_DOMAIN}/password_reset/{user.id}/{token}'
                        #email
                        subject = '[MPH 2019] Password change request'
                        html_message = render_to_string('PHapp/passwordChangeTemplate.html', {'teamName':team.teamName, 'username': user.username, 'resetLink':resetLink})
                        plain_message = strip_tags(html_message)
                        email_from = settings.EMAIL_HOST_USER

                        send_mail(subject, plain_message, email_from, [email], html_message=html_message)
                    except:
                        return render(request, 'PHapp/passwordChangeEmailDone.html', {'emailForm':emailForm, 'bad':True})

                    return render(request, 'PHapp/passwordChangeEmailDone.html', {'emailForm':emailForm, 'bad':False})
                else:
                    return render(request, 'PHapp/passwordChangeEmailDone.html', {'emailForm':emailForm, 'bad':True})

            else:
                emailForm = PasswordChangeEmail()
                return render(request, 'PHapp/passwordChangeEmail.html', {'emailForm':emailForm, 'wrong':True})

    else:
        emailForm = PasswordChangeEmail()
    
    return render(request, 'PHapp/passwordChangeEmail.html', {'emailForm':emailForm, 'wrong':False})

def passwordReset(request, userId, token):
    logout(request)
    try:
        tokenObj = ResetTokens.objects.get(token=token)
        user = tokenObj.user
        if not tokenObj.active or user.id != userId:
            return render(request, 'PHapp/passwordReset.html', {'linkExpired':True})
        team = Teams.objects.get(authClone=user)
    except:
        return render(request, 'PHapp/passwordReset.html', {'linkExpired':True})

    if request.method == 'POST':
        changeForm = SetPasswordForm(user, request.POST)
        if changeForm.is_valid():
            changeForm.save()
            tokenObj.active = False
            tokenObj.save()
            return render(request, 'PHapp/passwordResetDone.html')
    else:
        changeForm = SetPasswordForm(user)

    return render(request, 'PHapp/passwordReset.html', {'changeForm':changeForm, 'linkExpired':False, 'user':user, 'team':team})
