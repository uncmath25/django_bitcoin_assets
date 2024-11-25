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

IS_CLOSED_KEY = 'is_closed'
MATCH_ID_KEY = 'match_id'

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
    # prices[BITB_NAME] = HTTPClient.get_cnbc_quote(BITB_NAME)
    prices[MSTR_NAME] = HTTPClient.get_cnbc_quote(MSTR_NAME)
    # Temporary hack as option prices can not be scraped
    import os
    prices[IBIT_CALL_Jan_16_26_75_NAME] = float(os.environ['IBIT_CALL_Jan_16_26_75_PRICE'])
    prices[IBIT_CALL_Jan_16_26_100_NAME] = float(os.environ['IBIT_CALL_Jan_16_26_100_PRICE'])
    return prices

def _build_context_data(raw_transactions, prices):
    # Inputs
    transactions = _clean_transactions(raw_transactions)
    etf_transactions = _group_transactions(transactions, ETF_NAMES)
    stock_transactions = _group_transactions(transactions, STOCK_NAMES)
    # Current Cost Basis
    bitcoin_current_cost_basis = _compute_open_cost_basis(transactions[BITCOIN_NAME])
    etf_current_cost_basis = _compute_open_cost_basis(etf_transactions)
    stock_current_cost_basis = _compute_open_cost_basis(stock_transactions)
    total_current_cost_basis = bitcoin_current_cost_basis + etf_current_cost_basis + stock_current_cost_basis
    # Current Balance
    total_bitcoin = _compute_total_open_amount(transactions[BITCOIN_NAME])
    bitcoin_current_balance = prices[BITCOIN_NAME] * total_bitcoin
    etf_current_balance = _compute_grouped_current_balance(transactions, prices, ETF_NAMES)
    stock_current_balance = _compute_grouped_current_balance(transactions, prices, STOCK_NAMES)
    total_current_balance = bitcoin_current_balance + etf_current_balance + stock_current_balance
    # Unrealized Gains
    bitcoin_unrealized_gains = bitcoin_current_balance - bitcoin_current_cost_basis
    etf_unrealized_gains = etf_current_balance - etf_current_cost_basis
    stock_unrealized_gains = stock_current_balance - stock_current_cost_basis
    total_unrealized_gains = bitcoin_unrealized_gains + etf_unrealized_gains + stock_unrealized_gains
    # Realized Gains
    bitcoin_realized_gains = _compute_grouped_realized_gains(transactions, [BITCOIN_NAME])
    etf_realized_gains = _compute_grouped_realized_gains(transactions, ETF_NAMES)
    stock_realized_gains = _compute_grouped_realized_gains(transactions, STOCK_NAMES)
    total_realized_gains = bitcoin_realized_gains + etf_realized_gains + stock_realized_gains
    # Profits
    bitcoin_profit = bitcoin_unrealized_gains + bitcoin_realized_gains
    etf_profit = etf_unrealized_gains + etf_realized_gains
    stock_profit = stock_unrealized_gains + stock_realized_gains
    total_profit = bitcoin_profit + etf_profit + stock_profit
    # ROI
    # total_roi = _compute_grouped_roi(transactions, prices, [BITCOIN_NAME] + ETF_NAMES + STOCK_NAMES)
    # bitcoin_roi = _compute_grouped_roi(transactions, prices, [BITCOIN_NAME])
    # etf_roi = _compute_grouped_roi(transactions, prices, ETF_NAMES)
    # stock_roi = _compute_grouped_roi(transactions, prices, STOCK_NAMES)
    # Current Allocation
    bitcoin_current_allocation = bitcoin_current_balance / total_current_balance
    etf_current_allocation = etf_current_balance / total_current_balance
    stock_current_allocation = stock_current_balance / total_current_balance
    # Prices
    formatted_prices = {name: format_full_price(prices[name]) for name in prices}
    formatted_prices[BITCOIN_NAME] = format_price(prices[BITCOIN_NAME])
    # Bitcoin Counts
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
        'total_unrealized_gains': format_price(total_unrealized_gains),
        'bitcoin_unrealized_gains': format_price(bitcoin_unrealized_gains),
        'etf_unrealized_gains': format_price(etf_unrealized_gains),
        'stock_unrealized_gains': format_price(stock_unrealized_gains),
        'total_realized_gains': format_price(total_realized_gains),
        'bitcoin_realized_gains': format_price(bitcoin_realized_gains),
        'etf_realized_gains': format_price(etf_realized_gains),
        'stock_realized_gains': format_price(stock_realized_gains),
        'total_profit': format_price(total_profit),
        'bitcoin_profit': format_price(bitcoin_profit),
        'etf_profit': format_price(etf_profit),
        'stock_profit': format_price(stock_profit),
        # 'total_roi': format_perc(total_roi),
        # 'bitcoin_roi': format_perc(bitcoin_roi),
        # 'etf_roi': format_perc(etf_roi),
        # 'stock_roi': format_perc(stock_roi),
        'bitcoin_current_allocation': format_perc(bitcoin_current_allocation),
        'etf_current_allocation': format_perc(etf_current_allocation),
        'stock_current_allocation': format_perc(stock_current_allocation),
        'prices': formatted_prices,
        'total_bitcoin': format_bitcoin(total_bitcoin),
        'total_bitcoin_etf': format_bitcoin(total_bitcoin + etf_bitcoin),
        'bitcoin_cost_basis': format_price(bitcoin_cost_basis)
    }

def _clean_transactions(raw_transactions):
    transactions = {}
    for name in raw_transactions:
        sale_transactions = [t for t in raw_transactions[name] if t[TYPE_KEY] == SELL_VALUE]
        transactions[name] = []
        match_id = 0
        for transaction in raw_transactions[name]:
            if transaction[TYPE_KEY] != SELL_VALUE:
                found_match = False
                for sale_transaction in sale_transactions:
                    if transaction[AMOUNT_KEY] == sale_transaction[AMOUNT_KEY]:
                        transactions[name].append(_build_clean_transaction(transaction, match_id))
                        transactions[name].append(_build_clean_transaction(sale_transaction, match_id))
                        match_id += 1
                        sale_transactions.remove(sale_transaction)
                        found_match = True
                        break
                if not found_match:
                    transactions[name].append(_build_clean_transaction(transaction, -1))
    return transactions

def _build_clean_transaction(raw_transaction, match_id=-1):
    transaction = {}
    transaction[PRICE_KEY] = raw_transaction[PRICE_KEY]
    transaction[AMOUNT_KEY] = raw_transaction[AMOUNT_KEY]
    transaction[FEE_KEY] = raw_transaction[FEE_KEY]
    transaction[MATCH_ID_KEY] = match_id
    transaction[IS_CLOSED_KEY] = match_id >= 0
    transaction[TYPE_KEY] = raw_transaction[TYPE_KEY]
    return transaction

def _group_transactions(transactions, names_to_group):
    grouped_transactions = []
    for name in names_to_group:
        if name in transactions:
            grouped_transactions.extend(transactions[name])
    return grouped_transactions

def _compute_open_cost_basis(transactions):
    return sum([t[PRICE_KEY] * t[AMOUNT_KEY] for t in transactions if not t[IS_CLOSED_KEY]])

def _compute_total_open_amount(transactions):
    return sum([t[AMOUNT_KEY] for t in transactions if not t[IS_CLOSED_KEY]])

def _compute_grouped_current_balance(transactions, prices, names_to_group):
    current_balance = 0
    for name in names_to_group:
        if name in transactions:
            total_open_amount = sum([t[AMOUNT_KEY] for t in transactions[name] if not t[IS_CLOSED_KEY]])
            if total_open_amount > 0:
                current_balance += prices[name] * total_open_amount
    return current_balance

def _compute_grouped_realized_gains(transactions, names_to_group):
    realized_gains = 0
    for name in names_to_group:
        if name in transactions:
            closed_transactions = [t for t in transactions[name] if t[IS_CLOSED_KEY]]
            for match_id in range(len(closed_transactions) // 2):
                match_transactions = [t for t in closed_transactions if t[MATCH_ID_KEY] == match_id]
                assert len(match_transactions) == 2, f'There should be 2 transaction with match id: {match_id}'
                buy_t = [t for t in match_transactions if t[TYPE_KEY] != SELL_VALUE][0]
                sell_t = [t for t in match_transactions if t[TYPE_KEY] == SELL_VALUE][0]
                realized_gains += buy_t[AMOUNT_KEY] * (sell_t[PRICE_KEY] - buy_t[PRICE_KEY])
    return realized_gains

def _compute_grouped_roi(transactions, prices, names_to_group):
    end = 0
    start = 0
    for name in names_to_group:
        if name in transactions:
            closed_transactions = [t for t in transactions[name] if t[IS_CLOSED_KEY]]
            for match_id in range(len(closed_transactions) // 2):
                match_transactions = [t for t in closed_transactions if t[MATCH_ID_KEY] == match_id]
                assert len(match_transactions) == 2, f'There should be 2 transaction with match id: {match_id}'
                buy_t = [t for t in match_transactions if t[TYPE_KEY] != SELL_VALUE][0]
                sell_t = [t for t in match_transactions if t[TYPE_KEY] == SELL_VALUE][0]
                end += sell_t[AMOUNT_KEY] * sell_t[PRICE_KEY]
                start += buy_t[AMOUNT_KEY] * buy_t[PRICE_KEY]
            open_transactions = [t for t in transactions[name] if not t[IS_CLOSED_KEY]]
            start += sum([t[AMOUNT_KEY] * t[PRICE_KEY] for t in open_transactions])
            end += prices[name] * sum([t[AMOUNT_KEY] for t in open_transactions])
    return end / start - 1

def _compute_etf_bitcoin(transactions, names_to_group):
    bitcoin = 0
    for name in names_to_group:
        if name in transactions:
            total_open_amount = sum([t[AMOUNT_KEY] for t in transactions[name] if not t[IS_CLOSED_KEY]])
            bitcoin += get_bitcoin_per_share(name) * total_open_amount
    return bitcoin

def get_bitcoin_per_share(name):
    if name == IBIT_NAME:
        return 0.000568
    if name == BITB_NAME:
        return 0.000545
    raise Exception(f'{name} not supported!')
