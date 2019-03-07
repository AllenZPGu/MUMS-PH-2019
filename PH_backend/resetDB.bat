@echo off
set /p var=This will clear all team activity in the DB. Are you sure?? [Y/N]: 
if %var%== Y python manage.py runscript clearDBActivity
if not %var%== Y exit