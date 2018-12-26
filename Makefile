SHELL := /bin/bash

test:
	coverage run jobtracker/manage.py test jobtracker/
	coverage report

run:
	python jobtracker/manage.py runserver
