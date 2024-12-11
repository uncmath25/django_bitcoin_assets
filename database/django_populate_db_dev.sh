#!/bin/bash

python3 manage.py add_transaction BITCOIN BUY 2024-03-01 65432.10 0.12345678 321.89
python3 manage.py add_transaction BITCOIN BUY 2024-04-01 76543.21 0.87654321 432.56
python3 manage.py add_transaction IBIT BUY 2024-05-01 35.43 123 0
python3 manage.py add_transaction IBIT BUY 2024-06-01 37.56 76 0
python3 manage.py add_transaction IBIT BUY 2024-06-01 38.34 91 0
python3 manage.py add_transaction IBIT SELL 2024-08-01 41.32 76 0
python3 manage.py add_transaction IBIT SELL 2024-08-01 42.67 91 0
python3 manage.py add_transaction BITB BUY 2024-05-01 33.65 98 0
python3 manage.py add_transaction BITB SELL 2024-11-01 57.98 98 0
python3 manage.py add_transaction MSTR BUY 2024-06-01 210.98 321 0
python3 manage.py add_transaction IBIT_CALL_Jan_16_26_75 BUY 2024-07-01 11 1200 9.87

python3 manage.py add_price BITCOIN 2024-11-02 65555.43
python3 manage.py add_price IBIT 2024-11-02 54.32
python3 manage.py add_price MSTR 2024-11-02 321.89
python3 manage.py add_price IBIT_CALL_Jan_16_26_75 2024-11-02 10.56
