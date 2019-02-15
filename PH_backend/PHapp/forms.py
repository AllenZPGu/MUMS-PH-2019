from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SolveForm(forms.Form):
	guess = forms.CharField(label='Guess', max_length = 200)

class TeamRegForm(UserCreationForm):
	teamName = forms.CharField(max_length=50, help_text='Enter your team name as you want it displayed publicly.')
	teamEmail = forms.EmailField(max_length=254, required=False, help_text='Enter a teamwide email address, if you own one.')

	class Meta:
		model = User
		fields = ('username', 'password1', 'password2', 'teamName', 'teamEmail')

class IndividualRegForm(forms.Form):
	name = forms.CharField(max_length=100, label="",  widget=forms.TextInput(attrs={'placeholder': 'Name'}))
	email = forms.EmailField(max_length=254, label="",  widget=forms.TextInput(attrs={'placeholder': 'Email'}))
	aussie = forms.BooleanField(required=True, label="")
	melb = forms.BooleanField(required=True, label="")
