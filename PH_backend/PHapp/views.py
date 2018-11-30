from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.contrib.auth.models import User
from .models import Puzzles, Teams
from django.conf import settings
import json
import time
import random

def index(request):
	return render(request, 'PHapp/home.html')

def puzzles(request):
	return render(request, 'PHapp/puzzles.html')

def faq(request):
	return render(request, 'PHapp/faq.html')

def teams(request):
	return render(request, 'PHapp/home.html')