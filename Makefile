SHELL := /bin/bash

test:
	coverage run jobtracker/manage.py test jobtracker/

run:
	python jobtracker/manage.py runserver
