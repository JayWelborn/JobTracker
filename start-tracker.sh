#! /bin/bash

# 50 character string to use as temporary secret key
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)

cd "$( dirname "${BASH_SOURCE[0]}" )";
echo "Creating virtual environment...";
virtualenv -p python3 venv > /dev/null;
source venv/bin/activate > /dev/null;

echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null;
cd jobtracker;
mkdir jobtracker/secrets;
echo "$NEW_UUID" > jobtracker/secrets/django-secret.key;

echo "Performing Migrations..."
python manage.py makemigrations > /dev/null;
python manage.py migrate > /dev/null;

echo "Running tests..."
python manage.py test;

echo "Install Complete."
echo "Run with 'python manage.py runserver'"