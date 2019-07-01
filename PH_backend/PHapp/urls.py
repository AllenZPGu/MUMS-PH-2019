from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView
from . import views

#settings.STATIC_URL = '/static/'

urlpatterns = [
	path('', views.index),
	path('puzzles/', views.puzzles),
	path('puzzle/<str:puzzleURL>/', views.showPuzzle),
	path('solve/<str:title>/', views.solve),
	path('puzzlestats/<str:title>/', views.puzzleInfo),
	path('hints/<str:title>/', views.hints),
	path('registration/', views.teamReg),
	path('teams/', views.teams),
	path('team/<int:teamId>/', views.teamInfo),
	path('faq/', views.faq),
	path('rules/', views.rules),
	path('login/', views.loginCustom),
	path('logout/', views.logoutCustom),
	path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
	path('ajax/colourCube/', views.colourCube),
	path('debrief/', views.debrief),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)