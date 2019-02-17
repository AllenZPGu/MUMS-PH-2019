import datetime

def stripToLetters(inputStr):
	allAlph = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	outputStr = ''
	for char in inputStr:
		if char in allAlph:
			outputStr += char
	return outputStr.upper()

def releaseStage():
	startTime = datetime.datetime(2019, 4, 28, 12, 0)
	nowTime = datetime.datetime.now()
	stage = nowTime-startTime
	return stage.days

def checkListAllNone(aList):
	for i in aList:
		if i != None:
			return False
	return True