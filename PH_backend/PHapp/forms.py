from django import forms

class SolveForm(forms.Form):
	guess = forms.CharField(label='Guess', max_length = 200)