from django import forms
from django.forms import formset_factory, BaseFormSet
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .helperFunctions import *


class SolveForm(forms.Form):
	guess = forms.CharField(label='Guess', max_length = 200)

class TeamRegForm(UserCreationForm):
	teamName = forms.CharField(max_length=50, help_text='Enter your team name as you want it displayed publicly.', label="Team name", required=True)
	teamEmail = forms.EmailField(max_length=254, required=False, help_text='Enter a teamwide email address, if you have one.', label="Team email")

	class Meta:
		model = User
		fields = ('username', 'password1', 'password2', 'teamName', 'teamEmail')
		label = ('x', 'y', 'z', 'w', 'x')

class IndivRegForm(forms.Form):
	name = forms.CharField(max_length=100, label="",  widget=forms.TextInput(attrs={'placeholder': 'Name'}))
	email = forms.EmailField(max_length=254, label="",  widget=forms.TextInput(attrs={'placeholder': 'Email'}))
	aussie = forms.BooleanField(required = False, label="")
	melb = forms.BooleanField(required = False, label="")

class BaseIndivRegFormSet(BaseFormSet):
	def clean(self):
		if any(self.errors):
			return
		#checks that at least one form is filled
		namesList = [i.cleaned_data.get('name') for i in self.forms]
		emailsList = [i.cleaned_data.get('email') for i in self.forms]
		if checkListAllNone(namesList) or checkListAllNone(emailsList):
			raise forms.ValidationError("Please ensure at least one member's details are recorded.")


IndivRegFormSet = formset_factory(IndivRegForm, formset=BaseIndivRegFormSet, extra=10)
