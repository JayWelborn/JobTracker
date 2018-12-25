SHELL := /bin/bash

start:
	source ./venv/bin/activate

test: start
	python jobtracker/manage.py test jobtracker/

run: start
	python manage.py runserver
