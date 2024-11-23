#!/bin/bash

python3 manage.py collectstatic --noinput
uwsgi --ini wsgi.ini
