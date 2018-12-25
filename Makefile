SHELL := /bin/bash

test:
	python jobtracker/manage.py test jobtracker/

run:
	python manage.py runserver
