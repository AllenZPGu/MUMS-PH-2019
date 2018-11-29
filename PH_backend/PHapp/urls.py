from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	#url(r'^puzzle/$', views.puzzle, name='puzzles'),
	url(r'^puzzles/$', views.puzzles, name='puzzles'),
	path('puzzles/<path:path>/', views.specificPuzzle, name='specific puzzle'),
	url(r'^teams/$', views.teams, name='teams'),
	url(r'^faq/$', views.faq, name='faq'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)