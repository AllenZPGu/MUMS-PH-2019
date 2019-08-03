from PHapp.models import Puzzles

def run():
	alph = ['A','B','C','D','E', 'F']
	for act in [1,2,3,4,5,6]:
		for scene in [1,2,3,4,5]:
			actualScene = scene if scene != 5 else 'S'
			newPuzzle = Puzzles()
			newPuzzle.title = f'Placeholder {act}.{actualScene}'
			newPuzzle.act = act
			newPuzzle.scene = scene
			newPuzzle.pdfPath = newPuzzle.title
			newPuzzle.answer = f'ANSWER{alph[act-1]}{alph[scene-1]}'
			newPuzzle.winPun = f'Some Win Pun for Puzzle {act}.{actualScene}'
			newPuzzle.losePun = f'Some Lose Pun for Puzzle {act}.{actualScene}'
			newPuzzle.hint1 = f'Some Hint 1 for Puzzle {act}.{actualScene}'
			newPuzzle.hint2 = f'Some Hint 2 for Puzzle {act}.{actualScene}'
			newPuzzle.hint3 = f'Some Hint 3 for Puzzle {act}.{actualScene}'
			newPuzzle.releaseStatus = act
			newPuzzle.save()
			print(f'Done {act}.{actualScene}')