import datetime
import pytz

AEST = pytz.timezone("Australia/Melbourne")
RELEASE_TIMES = [AEST.localize(datetime.datetime(2019, 8, 1, 0)) + datetime.timedelta(days=i) for i in range(10)]
PUZZLE_COLOURS = [
	['W','O','','','G','',], ['O','W','','','','',], ['W','O','B','','','',],
	['Y','','','','O','',],  ['R','','','','','',],  ['G','','O','','','',],
	['B','','','Y','R','',], ['G','','','Y','','',], ['W','','R','G','','',],
	['','W','','','B','',],  ['','B','','','','',],  ['','B','R','','','',],
	['','','','','W','',],   ['','','','','','',],   ['','','Y','','','',],
	['','','','R','Y','',],  ['','','','G','','',],  ['','','B','O','','',],
	['','Y','','','O','G',], ['','G','','','','R',], ['','W','R','','','B',],
	['','','','','G','W',],  ['','','','','','O',],  ['','','W','','','R',],
	['','','','O','B','Y',], ['','','','B','','Y',], ['','','Y','R','','G',],
]
PUZZLE_COLOURS_BLANK = [
	['A','A','','','A','',], ['A','A','','','','',], ['A','A','A','','','',],
	['A','','','','A','',],  ['A','','','','','',],  ['A','','A','','','',],
	['A','','','A','A','',], ['A','','','A','','',], ['A','','A','A','','',],
	['','A','','','A','',],  ['','A','','','','',],  ['','A','A','','','',],
	['','','','','A','',],   ['','','','','','',],   ['','','A','','','',],
	['','','','A','A','',],  ['','','','A','','',],  ['','','A','A','','',],
	['','A','','','A','A',], ['','A','','','','A',], ['','A','A','','','A',],
	['','','','','A','A',],  ['','','','','','A',],  ['','','A','','','A',],
	['','','','A','A','A',], ['','','','A','','A',], ['','','A','A','','A',],
]
PUZZLE_TEXTS = [
	['1','3','','','2','',], ['','','','','','',],   ['2','4','1','','','',],
	['','','','','','',],    ['I','','','','','',],  ['','','','','','',],
	['3','','','1','4','',], ['','','','','','',],   ['4','','3','2','','',],
	['','','','','','',],    ['','VI','','','','',],  ['','','','','','',],
	['','','','','II',''],   ['','','','','','',],   ['','','IV','','','',],
	['','','','','','',],    ['','','','V','','',], ['','','','','','',],
	['','1','','','1','2',], ['','','','','','',],   ['','2','2','','','1',],
	['','','','','','',],    ['','','','','','III',], ['','','','','','',],
	['','','','3','3','4',], ['','','','','','',],   ['','','4','4','','2',],
]

CUBE_CELL_MAP = (
	(),
	((),  (0, 0),  (2, 0),  (6, 0),  (8, 0),  (4, 0)), # F
	((), (18, 4),  (0, 4), (24, 4),  (6, 4), (12, 4)), # L
	((), (20, 5), (18, 5), (26, 5), (24, 5), (22, 5)), # B
	((),  (2, 2), (20, 2),  (8, 2), (26, 2), (14, 2)), # R
	((),  (6, 3),  (8, 3), (24, 3), (26, 3), (16, 3)), # D
	((), (18, 1), (20, 1),  (0, 1),  (2, 1), (10, 1)), # U
)