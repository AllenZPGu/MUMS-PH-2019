import datetime

def stripToLetters(inputStr):
	allAlph = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	outputStr = ''
	for char in inputStr:
		if char in allAlph:
			outputStr += char
	return outputStr.lower()

def releaseStage():
	startTime = datetime.datetime(2019, 4, 28, 12, 0)
	nowTime = datetime.datetime.now()
	stage = nowTime-startTime
	return stage.days