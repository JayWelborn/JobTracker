# JobTracker 

[![Build Status](https://travis-ci.com/JayWelborn/JobTracker.svg?token=r3JkfftxGDq6gFug9hF1&branch=master)](https://travis-ci.com/JayWelborn/JobTracker)
[![codecov](https://codecov.io/gh/JayWelborn/JobTracker/branch/master/graph/badge.svg)](https://codecov.io/gh/JayWelborn/JobTracker)

This is a simple job application tracking system, designed to save time spent
keeping track of the status of multiple applications.

***WORK IN PROGRESS***

## About

JobTracker uses the [Finite State Machine](https://en.wikipedia.org/wiki/Finite-state_machine)
pattern to track a job application from submission to accepting a job offer
JobTracker is meant to simplify the process of applying to and interviewing
jobs by providing a one-stop dashboard for your job search.

### Backend

- [Django](https://www.djangoproject.com/) and
  [DjangoRestFramework](https://www.django-rest-framework.org) for API

- [Virtualenv](https://virtualenv.pypa.io/en/latest/) and 
  [pip](https://pip.pypa.io/en/stable/) to manage Python dependencies
- [django-fsm](https://github.com/viewflow/django-fsm) and
  [drf-fsm-transitions](https://github.com/jacobh/drf-fsm-transitions) to model
  finite state machine
- [TravisCI](https://travis-ci.com/) for testing on each commit
- [CodeCov](https://codecov.io/) to track test coverage over time

### Frontend

- [React](https://reactjs.org) for single-page app
- [SASS/SCSS](https://sass-lang.com/) for styling

## Requirements
JobTracker requires you to have Python 3.5+ and virtualenv installed on your
machine. The install script assumes you are in a UNIX environment. If you are
running the project from a different operating system, you will need to install
the requirements manually

JobTracker is tested for Python 3.5+

## How to install

```bash
$ git clone https://github.com/JayWelborn/JobTracker.git
$ cd JobTracker
$ ./start-tracker.sh
```

## Deployment

It is possible to deploy to Heroku or to your own server.

## License
    
    Copyright (C) 2018 Jay Welborn
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.