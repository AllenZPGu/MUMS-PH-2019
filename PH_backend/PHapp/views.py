from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
import time
import random

def index(request):
	return render(request, 'PHapp/home.html')

def puzzles(request):
	return render(request, 'PHapp/puzzles.html')