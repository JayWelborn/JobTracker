SHELL := /bin/bash

test:
	coverage run jobtracker/manage.py test jobtracker/
	coverage report --fail-under=95
	coverage html

run:
	python jobtracker/manage.py runserver
