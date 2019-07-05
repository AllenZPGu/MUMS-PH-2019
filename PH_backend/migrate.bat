CALL ../PHenv/Scripts/activate.bat
python manage.py makemigrations
pause
python manage.py migrate --database=development
python manage.py migrate --database=live
pause