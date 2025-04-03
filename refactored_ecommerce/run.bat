@echo off
echo Starting E-commerce Application...
echo.

echo Creating data directories if they don't exist...
if not exist "data" mkdir data

echo Setting up the environment...
python -m pip install -r requirements.txt

echo Migrating databases...
python manage.py makemigrations
python manage.py migrate

echo Starting the server...
python manage.py runserver 0.0.0.0:8000

pause 