#JobTracker [![Build Status](https://travis-ci.com/JayWelborn/JobTracker.svg?token=r3JkfftxGDq6gFug9hF1&branch=master)](https://travis-ci.com/JayWelborn/JobTracker) #+html: <img src="coverage.svg" />

This is a simple job application tracking system, designed to save time spent
keeping track of the status of multiple applications.

## About

JobTracker uses the [Finite State Machine](https://en.wikipedia.org/wiki/Finite-state_machine)
pattern to track a job application from submission to accepting a job offer
JobTracker is meant to simplify the process of applying to and interviewing
jobs by providing a one-stop dashboard for your job search.

## Features

- Django 2.0+
- Uses [Virtualenv](https://virtualenv.pypa.io/en/latest/) and 
  [pip](https://pip.pypa.io/en/stable/) to manage dependencies.
- Uses [django-fsm](https://github.com/viewflow/django-fsm) and
  [drf-fsm-transitions](https://github.com/jacobh/drf-fsm-transitions) to model
  finite state machine.
- HTTPS and other security related settings on Staging and Production.

## Requirements
JobTracker requires you to have Python 3.5+ and virtualenv installed on your
machine. The install script assumes you are in a UNIX environment. If you are
running the project from a different operating system, you will need to install
the requirements manually

## How to install

```bash
$ git clone https://github.com/JayWelborn/JobTracker.git
$ cd JobTracker
$ ./start-tracker.sh
```

## Deployment

It is possible to deploy to Heroku or to your own server.

## License

The MIT License (MIT)

Copyright (c) 2012-2017 José Padilla

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.