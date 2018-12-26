SHELL := /bin/bash

test:
	coverage run jobtracker/manage.py test jobtracker/
	rm -f coverage.svg
	coverage-badge -o coverage.svg

run:
	python jobtracker/manage.py runserver
