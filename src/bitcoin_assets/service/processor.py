from ..models import Transaction
from .http_client import HTTPClient
from .utils import format_bitcoin, format_full_price, format_perc, format_price


BITCOIN_NAME = 'BITCOIN'
IBIT_NAME = 'IBIT'
BITB_NAME = 'BITB'
MSTR_NAME = 'MSTR'
IBIT_CALL_Jan_16_26_75_NAME = 'IBIT_CALL_Jan_16_26_75'
IBIT_CALL_Jan_16_26_100_NAME = 'IBIT_CALL_Jan_16_26_100'

ETF_NAME = 'ETF'
STOCK_NAME = 'STOCK'
ETF_NAMES = [IBIT_NAME, BITB_NAME]
STOCK_NAMES = [MSTR_NAME, IBIT_CALL_Jan_16_26_75_NAME, IBIT_CALL_Jan_16_26_100_NAME]

NAME_KEY = 'name'
TYPE_KEY = 'type'
PRICE_KEY = 'price'
AMOUNT_KEY = 'amount'
FEE_KEY = 'fee'

SELL_VALUE = 'SELL'

IS_BUY_KEY = 'is_buy'
IS_CLOSED_KEY = 'is_closed'

# Assume that all sell transaction actually match 1 buy transaction
# Is a valid reduction, as all "buy = sell + buy (at sell price)"

def build_context():
    transactions = _get_transactions()
    prices = _get_prices()
    return _build_context_data(transactions, prices)

def _get_transactions():
    transactions = {}
    for r in Transaction.objects.values():
        d = {}
        d[PRICE_KEY] = float(r[PRICE_KEY])
        d[AMOUNT_KEY] = float(r[AMOUNT_KEY])
        d[FEE_KEY] = float(r[FEE_KEY])
        d[TYPE_KEY] = str(r[TYPE_KEY])
        name = str(r[NAME_KEY])
        if name not in transactions:
            transactions[name] = [d]
        else:
            transactions[name].append(d)
    return transactions

def _get_prices():
    prices = {}
    prices[BITCOIN_NAME] = HTTPClient.get_bitcoin_price()
    prices[IBIT_NAME] = HTTPClient.get_cnbc_quote(IBIT_NAME)
    prices[BITB_NAME] = HTTPClient.get_cnbc_quote(BITB_NAME)
    prices[MSTR_NAME] = HTTPClient.get_cnbc_quote(MSTR_NAME)
    # Temporary hack as option prices can not be scraped
    import os
    prices[IBIT_CALL_Jan_16_26_75_NAME] = float(os.environ['IBIT_CALL_Jan_16_26_75_PRICE'])
    prices[IBIT_CALL_Jan_16_26_100_NAME] = float(os.environ['IBIT_CALL_Jan_16_26_100_PRICE'])
    return prices

def _build_context_data(raw_transactions, prices):
    transactions = _clean_transactions(raw_transactions)
    etf_transactions = _group_transactions(transactions, ETF_NAMES)
    stock_transactions = _group_transactions(transactions, STOCK_NAMES)
    bitcoin_current_cost_basis = _compute_open_cost_basis(transactions[BITCOIN_NAME])
    etf_current_cost_basis = _compute_open_cost_basis(etf_transactions)
    stock_current_cost_basis = _compute_open_cost_basis(stock_transactions)
    total_current_cost_basis = bitcoin_current_cost_basis + etf_current_cost_basis + stock_current_cost_basis
    total_bitcoin = _compute_total_open_amount(transactions[BITCOIN_NAME])
    bitcoin_current_balance = prices[BITCOIN_NAME] * total_bitcoin
    etf_current_balance = _compute_grouped_current_balance(transactions, prices, ETF_NAMES)
    stock_current_balance = _compute_grouped_current_balance(transactions, prices, STOCK_NAMES)
    total_current_balance = bitcoin_current_balance + etf_current_balance + stock_current_balance
    etf_bitcoin = _compute_etf_bitcoin(transactions, ETF_NAMES)
    bitcoin_cost_basis = sum([r[AMOUNT_KEY] * r[PRICE_KEY] for r in transactions[BITCOIN_NAME]]) \
        / sum([r[AMOUNT_KEY] for r in transactions[BITCOIN_NAME]])
    return {
        'total_current_cost_basis': format_price(total_current_cost_basis),
        'bitcoin_current_cost_basis': format_price(bitcoin_current_cost_basis),
        'etf_current_cost_basis': format_price(etf_current_cost_basis),
        'stock_current_cost_basis': format_price(stock_current_cost_basis),
        'total_current_balance': format_price(total_current_balance),
        'bitcoin_current_balance': format_price(bitcoin_current_balance),
        'etf_current_balance': format_price(etf_current_balance),
        'stock_current_balance': format_price(stock_current_balance),
        'total_bitcoin': format_bitcoin(total_bitcoin),
        'total_bitcoin_etf': format_bitcoin(total_bitcoin + etf_bitcoin),
        'bitcoin_cost_basis': format_price(bitcoin_cost_basis),
        'bitcoin_price': format_price(prices[BITCOIN_NAME]),
        'ibit_price': format_full_price(prices[IBIT_NAME]),
        'bitb_price': format_full_price(prices[BITB_NAME]),
        'mstr_price': format_full_price(prices[MSTR_NAME]),
        'ibit_call_1_price': format_full_price(prices[IBIT_CALL_Jan_16_26_75_NAME]),
        'ibit_call_2_price': format_full_price(prices[IBIT_CALL_Jan_16_26_100_NAME])
    }

def _clean_transactions(raw_transactions):
    transactions = {}
    for name in raw_transactions:
        sale_transactions = [r[AMOUNT_KEY] for r in raw_transactions[name] if r[TYPE_KEY] == SELL_VALUE]
        transactions[name] = []
        for transaction in raw_transactions[name]:
            if transaction[TYPE_KEY] != SELL_VALUE:
                amount = transaction[AMOUNT_KEY]
                if amount in sale_transactions:
                    sale_transactions.remove(amount)
                    transactions[name].append(_build_clean_transaction(transaction, True))
                else:
                    transactions[name].append(_build_clean_transaction(transaction, False))
            else:
                transactions[name].append(_build_clean_transaction(transaction, True))
    return transactions

def _build_clean_transaction(raw_transaction, is_closed):
    transaction = {}
    transaction[PRICE_KEY] = raw_transaction[PRICE_KEY]
    transaction[AMOUNT_KEY] = raw_transaction[AMOUNT_KEY]
    transaction[FEE_KEY] = raw_transaction[FEE_KEY]
    transaction[IS_BUY_KEY] = raw_transaction[TYPE_KEY] != SELL_VALUE
    transaction[IS_CLOSED_KEY] = is_closed
    return transaction

def _group_transactions(transactions, names_to_group):
    grouped_transactions = []
    for name in names_to_group:
        if name in transactions:
            grouped_transactions.extend(transactions[name])
    return grouped_transactions

def _compute_open_cost_basis(transactions):
    return sum([r[PRICE_KEY] * r[AMOUNT_KEY] for r in transactions if not r[IS_CLOSED_KEY]])

def _compute_total_open_amount(transactions):
    return sum([r[AMOUNT_KEY] for r in transactions if not r[IS_CLOSED_KEY]])

def _compute_grouped_current_balance(transactions, prices, names_to_group):
    current_balance = 0
    for name in names_to_group:
        if name in transactions:
            total_open_amount = sum([r[AMOUNT_KEY] for r in transactions[name] if not r[IS_CLOSED_KEY]])
            current_balance += prices[name] * total_open_amount
    return current_balance

def _compute_etf_bitcoin(transactions, names_to_group):
    bitcoin = 0
    for name in names_to_group:
        if name in transactions:
            total_open_amount = sum([r[AMOUNT_KEY] for r in transactions[name] if not r[IS_CLOSED_KEY]])
            bitcoin += get_bitcoin_per_share(name) * total_open_amount
    return bitcoin

def get_bitcoin_per_share(name):
    if name == IBIT_NAME:
        return 0.000568
    if name == BITB_NAME:
        return 0.000545
    raise Exception(f'{name} not supported!')
