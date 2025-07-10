#!/bin/bash

python3 manage.py add_asset BITCOIN
python3 manage.py add_asset IBIT
python3 manage.py add_asset BITB
python3 manage.py add_asset MSTR
python3 manage.py add_asset MTPLF
python3 manage.py add_asset IBIT_CALL_Jan_16_26_75

python3 manage.py add_transaction 1 0 2024-03-01 65432.10 0.12345678 321.89
python3 manage.py add_transaction 1 0 2024-04-01 76543.21 0.87654321 432.56
python3 manage.py add_transaction 2 0 2024-05-01 35.43 123 0
python3 manage.py add_transaction 2 0 2024-06-01 37.56 76 0
python3 manage.py add_transaction 2 0 2024-06-01 38.34 91 0
python3 manage.py add_transaction 2 1 2024-08-01 41.32 76 0
python3 manage.py add_transaction 2 1 2024-08-01 42.67 91 0
python3 manage.py add_transaction 3 0 2024-05-01 33.65 98 0
python3 manage.py add_transaction 3 1 2024-11-01 57.98 98 0
python3 manage.py add_transaction 4 0 2024-06-01 210.98 321 0
python3 manage.py add_transaction 5 0 2024-06-01 2.34 1234 0
python3 manage.py add_transaction 6 0 2024-07-01 11 1200 9.87

python3 manage.py add_price 1 2024-11-02 65555.43
python3 manage.py add_price 2 2024-11-02 54.32
python3 manage.py add_price 4 2024-11-02 321.89
python3 manage.py add_price 5 2024-11-02 4.56
python3 manage.py add_price 6 2024-11-02 10.56
