/*


	COLORS

	Here's a little bootstrapping to create our global Color constants.
	At first it seemed like overkill, but then as the solvers and inspectors
	moved forward having these objects available became highly desirable.
	Sure, ES5 doesn't really have constants but the all-caps alerts you
	to the fact that them thar variables ought not to be messed with.


*/












function Color( name, initial, hex, styleF, styleB ){

	this.name    = name
	this.initial = initial
	this.hex     = hex
	this.styleF  = styleF
	this.styleB  = styleB
}


//  Global constants to describe sticker colors.

var
W = WHITE = new Color(

	'white',
	'W',
	'#FFF',
	'font-weight: bold; color: #888',
	'background-color: #F3F3F3; color: rgba( 0, 0, 0, 0.5 )'
),
O = ORANGE = new Color(

	'orange',
	'O',
	'#F60',
	'font-weight: bold; color: #F60',
	'background-color: #F60; color: rgba( 255, 255, 255, 0.9 )'
),
B = BLUE = new Color(

	'blue',
	'B',
	'#00D',
	'font-weight: bold; color: #00D',
	'background-color: #00D; color: rgba( 255, 255, 255, 0.9 )'
),
R = RED = new Color(

	'red',
	'R',
	'#F00',
	'font-weight: bold; color: #F00',
	'background-color: #F00; color: rgba( 255, 255, 255, 0.9 )'
),
G = GREEN = new Color(

	'green',
	'G',
	'#33CC33',
	'font-weight: bold; color: #33CC33',
	'background-color: #33CC33; color: rgba( 255, 255, 255, 0.9 )'
),
Y = YELLOW = new Color(

	'yellow',
	'Y',
	'#FE0',
	'font-weight: bold; color: #ED0',
	'background-color: #FE0; color: rgba( 0, 0, 0, 0.5 )'
),
A = GRAY = new Color(
	'gray',
	'A',
	'#777',
	'font-weight: bold; color: #666',
	'background-color: #777; color: rgba(0,0,0,0.5)'
),
P = PURPLE = new Color(
	'purple',
	'P',
	'#F0F',
	'font-weight: bold; color: #E0E',
	'background-color: #F0F; color: rgba(255, 255, 255, 0.9)'
),
COLORLESS = new Color(

	'NA',
	'X',
	'#DDD',
	'color: #EEE',
	'color: #DDD'
)

var COLORMAP = {'W': W, 'O': O, 'B': B, 'R': R, 'G': G, 'Y': Y, 'A': A, 'P': P, '': COLORLESS}

