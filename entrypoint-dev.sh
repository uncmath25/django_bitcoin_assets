#!/bin/bash
python3 manage.py makemigrations bitcoin_assets
python3 manage.py migrate
sleep 1
python3 manage.py add_bitcoin_transaction 2024-03-01 65432.10 0.12345678 66666.66
python3 manage.py add_bitcoin_transaction 2024-04-01 76543.21 0.87654321 77777.77
python3 manage.py collectstatic --noinput
python3 manage.py runserver 0.0.0.0:8000
