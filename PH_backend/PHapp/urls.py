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
	path('puzzle/<str:puzzleURL>', views.showPuzzle),
	path('solve/<str:chapter>/<str:status>/', views.solve),
	path('registration/', views.teamReg),
	path('teams/', views.teams),
	path('faq/', views.faq),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)