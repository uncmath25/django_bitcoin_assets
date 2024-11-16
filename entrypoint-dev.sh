#!/bin/bash
python3 manage.py makemigrations bitcoin_assets
python3 manage.py migrate
sleep 1
python3 manage.py add_transaction trans_1
python3 manage.py add_transaction trans_2
python3 manage.py add_transaction trans_3
python3 manage.py runserver 0.0.0.0:8000
