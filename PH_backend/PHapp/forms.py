from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .helperFunctions import *
from .models import Teams

class SolveForm(forms.Form):
	guess = forms.CharField(label='Guess', max_length = 200)

# class TeamRegForm(forms.Form):
# 	teamName = forms.CharField(max_length=50, 
# 		help_text='Enter your team name as you want it displayed publicly.', label="Team name", required=True)
# 	teamEmail = forms.EmailField(max_length=254, required=False, 
# 		help_text='Enter a teamwide email address, if you have one.', label="Team email")

class TeamRegForm(forms.ModelForm):
	class Meta:
		model = Teams
		fields = ['teamName', 'teamEmail']
		help_texts = {'teamName': 'Enter your team name as you want it displayed publicly.',
			'teamEmail':'Enter a teamwide email address, if you have one. This will be kept confidential.'}
		labels = {'teamName':'Team name', 'teamEmail':'Team email'}
		error_messages = {'teamName':{'unique':'This team name has already been taken.'},
			'teamEmail':{'unique':'This team email has already been taken.'}}

class IndivRegForm(forms.Form):
	name = forms.CharField(max_length=100, label="",  widget=forms.TextInput(attrs={'placeholder': 'Name'}))
	email = forms.EmailField(max_length=254, label="",  widget=forms.TextInput(attrs={'placeholder': 'Email'}))
	aussie = forms.BooleanField(required = False, label="")
	melb = forms.BooleanField(required = False, label="")

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', help_text='Please enter your username and NOT your team name. This is case-sensitive.')
	password = forms.CharField(widget=forms.PasswordInput, label='Password', help_text='This is case-sensitive.')

class BaseIndivRegFormSet(forms.BaseFormSet):
	def clean(self):
		if any(self.errors):
			return
		#checks that at least one form is filled
		namesList = [i.cleaned_data.get('name') for i in self.forms]
		emailsList = [i.cleaned_data.get('email') for i in self.forms]
		if checkListAllNone(namesList) or checkListAllNone(emailsList):
			raise forms.ValidationError("Please ensure that at least one member's details are recorded.")

IndivRegFormSet = forms.formset_factory(IndivRegForm, formset=BaseIndivRegFormSet, extra=10)
