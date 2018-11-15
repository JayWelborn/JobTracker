#! /bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )";
gnome-terminal;
source venv/bin/activate;
cd jobtracker;
python manage.py runserver;