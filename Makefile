SHELL := /bin/bash

test:
	coverage run jobtracker/manage.py test jobtracker/
	coverage report --fail-under=90

run:
	python jobtracker/manage.py runserver
