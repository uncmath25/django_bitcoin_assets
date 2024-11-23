#!/bin/bash

python3 manage.py makemigrations bitcoin_assets
python3 manage.py migrate
sleep 1
/django_populate_db_dev.sh
python3 manage.py collectstatic --noinput
python3 manage.py runserver 0.0.0.0:8000
