import datetime

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