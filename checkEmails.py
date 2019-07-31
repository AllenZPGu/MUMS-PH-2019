with open('emails.csv', 'r') as f:
	x = []
	for i in f:
		y = i.split(',')[1][:-1]
		if y not in x:
			x.append(y)
	x.sort()
	print(x)
	print(len(x))
