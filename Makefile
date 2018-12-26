SHELL := /bin/bash

test:
	coverage run jobtracker/manage.py test jobtracker/
	coverage html --fail-under=95

run:
	python jobtracker/manage.py runserver
