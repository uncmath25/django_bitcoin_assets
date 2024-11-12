#!/bin/bash
python3 src/manage.py collectstatic --noinput
uwsgi --ini src/wsgi.ini
