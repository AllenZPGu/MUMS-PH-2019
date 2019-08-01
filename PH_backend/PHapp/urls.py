from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from . import views
from .helperFunctions import IntToRoman

#settings.STATIC_URL = '/static/'

urlpatterns = [
	path('', views.index),
	path('index.html', views.index),
	path('puzzles/', views.puzzles),
	path('puzzles/<int:act>/<int:scene>/', lambda req, act, scene: redirect(views.showPuzzle, act=IntToRoman(act), scene=scene, puzzleName='Placeholder', permanent=True)),
	path('puzzles/<int:act>/S/', lambda req, act, scene: redirect(views.showPuzzleMiniMeta, act=IntToRoman(act), puzzleName='Placeholder', permanent=True)),
	path('puzzles/<str:act>/<int:scene>/', lambda req, act, scene: redirect(views.showPuzzle, act=act, scene=scene, puzzleName='Placeholder', permanent=True)),
	path('puzzles/<str:act>/S/', lambda req, act, scene: redirect(views.showPuzzleMiniMeta, act=act, puzzleName='Placeholder', permanent=True)),
	path('puzzles/<str:act>.<int:scene> <str:puzzleName>.pdf', views.showPuzzle),
	path('puzzles/<str:act>.S <str:puzzleName>.pdf', views.showPuzzleMiniMeta),
	path('puzzles/meta/', lambda req: redirect(views.showPuzzleMeta, permanent=True)),
	path('puzzles/Meta.pdf', views.showPuzzleMeta),
	path('solve/<int:act>/<int:scene>/', lambda req, act, scene: redirect(views.solve, act=IntToRoman(act), scene=scene, permanent=True)),
	path('solve/<int:act>/S/', lambda req, act: redirect(views.solveMiniMeta, act=IntToRoman(act), permanent=True)),
	path('solve/<str:act>/<int:scene>/', views.solve),
	path('solve/<str:act>/S/', views.solveMiniMeta),
	path('solve/meta/', views.solveMeta),
	path('puzzlestats/<int:act>/<int:scene>/', lambda req, act, scene: redirect(views.puzzleInfo, act=IntToRoman(act), scene=scene, permanent=True)),
	path('puzzlestats/<int:act>/S/', lambda req, act: redirect(views.puzzleInfoMiniMeta, act=IntToRoman(act), permanent=True)),
	path('puzzlestats/<str:act>/<int:scene>/', views.puzzleInfo),
	path('puzzlestats/<str:act>/S/', views.puzzleInfoMiniMeta),
	path('puzzlestats/meta/', views.puzzleInfoMeta),
	path('hints/<int:act>/<int:scene>/', lambda req, act, scene: redirect(views.hints, act=IntToRoman(act), scene=scene, permanent=True)),
	path('hints/<int:act>/S/', lambda req, act: redirect(views.hintsMiniMeta, act=IntToRoman(act), permanent=True)),
	path('hints/<str:act>/<int:scene>/', views.hints),
	path('hints/<str:act>/S/', views.hintsMiniMeta),
	path('hints/meta/', views.hintsMeta),
	path('registration/', views.teamReg),
	path('teams/', views.teams),
	path('team/<int:teamId>/', views.teamInfo),
	path('teamEdit/', views.editTeamMembers),
	path('faq/', views.faq),
	path('rules/', views.rules),
	path('login/', views.loginCustom),
	path('logout/', views.logoutCustom),
	path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
	path('dynamic/cubedata.js', views.cubeData),
	path('debrief/', views.debrief),
	path('announcements/', views.announcements)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)