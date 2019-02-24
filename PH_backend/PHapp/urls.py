from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

#settings.STATIC_URL = '/static/'

urlpatterns = [
	path('', views.index),
	path('puzzles/', views.puzzles),
	path('puzzle/<str:puzzleURL>/', views.showPuzzle),
	path('solve/<str:title>/', views.solve),
	path('stats/<str:title>/', views.stats),
	path('hints/<str:title>/', views.hints),
	path('registration/', views.teamReg),
	path('teams/', views.teams),
	path('team/<int:teamId>/', views.teamInfo),
	path('faq/', views.faq),
	path('about/', views.about),
	path('login/', views.loginCustom),
	path('logout/', views.logoutCustom)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)