from ..models import Transaction
from .http_client import HTTPClient
from .utils import format_bitcoin, format_full_price, format_perc, format_price


BITCOIN_CATEGORY = 'Bitcoin'
ETF_CATEGORY = 'ETF'
STOCKS_CATEGORY = 'Stocks'
OPTIONS_CATEGORY = 'Options'
TOTAL_CATEGORY = 'Total'
BITCOIN_NAME = 'BITCOIN'
IBIT_NAME = 'IBIT'
BITB_NAME = 'BITB'
INVESTMENTS = {
    BITCOIN_CATEGORY: [BITCOIN_NAME],
    ETF_CATEGORY: [IBIT_NAME, BITB_NAME],
    STOCKS_CATEGORY: ['MSTR'],
    OPTIONS_CATEGORY: ['IBIT_CALL_Jan_16_26_75', 'IBIT_CALL_Jan_16_26_100']
}
TOTAL_CATEGORIES = [TOTAL_CATEGORY] + list(INVESTMENTS.keys())

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
    transactions = _clean_transactions(_get_raw_transactions())
    prices = _get_prices(transactions)
    return _build_context_data(transactions, prices)

def _get_raw_transactions():
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

def _get_prices(transactions):
    open_investments = [name for name in transactions
        if len([t for t in transactions[name] if not t[IS_CLOSED_KEY]]) > 0]
    prices = {}
    for category in INVESTMENTS:
        for name in INVESTMENTS[category]:
            if name not in open_investments:
                continue
            if category == BITCOIN_CATEGORY:
                prices[BITCOIN_NAME] = HTTPClient.get_bitcoin_price()
            elif category == OPTIONS_CATEGORY:
                prices[name] = HTTPClient.get_option_price(name)
            else:
                prices[name] = HTTPClient.get_cnbc_quote(name)
    return prices

def _build_context_data(transactions, prices):
    current_cost_bases = _compute_metric(transactions, prices, _compute_open_cost_basis)
    current_balances = _compute_metric(transactions, prices, _compute_grouped_current_balance)
    unrealized_gains = {c: current_balances[c] - current_cost_bases[c] for c in INVESTMENTS}
    realized_gains = _compute_metric(transactions, prices, _compute_grouped_realized_gains)
    profits = {c: realized_gains[c] + unrealized_gains[c] for c in INVESTMENTS}
    allocations = {c: current_balances[c] / sum(current_balances.values()) for c in INVESTMENTS}
    total_bitcoin = _compute_total_bitcoin(transactions)
    return {
        'categories': TOTAL_CATEGORIES,
        'current_cost_bases': _format_metric(current_cost_bases),
        'current_balances': _format_metric(current_balances),
        'unrealized_gains': _format_metric(unrealized_gains),
        'realized_gains': _format_metric(realized_gains),
        'profits': _format_metric(profits),
        'allocations': _format_perc(allocations),
        'prices': _build_formatted_prices(prices),
        'total_bitcoin': format_bitcoin(total_bitcoin),
        'total_bitcoin_etf': format_bitcoin(total_bitcoin + _compute_etf_bitcoin(transactions)),
        'bitcoin_cost_basis': format_price(_compute_bitcoin_cost_basis(transactions))
    }

def _compute_metric(transactions, prices, metric_fcn):
    return {category: metric_fcn(transactions, prices, category) for category in INVESTMENTS}

def _compute_open_cost_basis(transactions, _, category):
    grouped_transactions = _group_transactions(transactions, INVESTMENTS[category])
    return sum([t[PRICE_KEY] * t[AMOUNT_KEY] for t in grouped_transactions if not t[IS_CLOSED_KEY]])

def _group_transactions(transactions, names_to_group):
    grouped_transactions = []
    for name in names_to_group:
        if name in transactions:
            grouped_transactions.extend(transactions[name])
    return grouped_transactions

def _compute_grouped_current_balance(transactions, prices, category):
    current_balance = 0
    for name in INVESTMENTS[category]:
        if name in transactions:
            total_open_amount = sum([t[AMOUNT_KEY] for t in transactions[name] if not t[IS_CLOSED_KEY]])
            if total_open_amount > 0:
                current_balance += prices[name] * total_open_amount
    return current_balance

def _compute_grouped_realized_gains(transactions, _, category):
    realized_gains = 0
    for name in INVESTMENTS[category]:
        if name in transactions:
            closed_transactions = [t for t in transactions[name] if t[IS_CLOSED_KEY]]
            for match_id in range(len(closed_transactions) // 2):
                match_transactions = [t for t in closed_transactions if t[MATCH_ID_KEY] == match_id]
                assert len(match_transactions) == 2, f'There should be 2 transaction with match id: {match_id}'
                buy_t = [t for t in match_transactions if t[TYPE_KEY] != SELL_VALUE][0]
                sell_t = [t for t in match_transactions if t[TYPE_KEY] == SELL_VALUE][0]
                realized_gains += buy_t[AMOUNT_KEY] * (sell_t[PRICE_KEY] - buy_t[PRICE_KEY])
    return realized_gains

# def _compute_grouped_roi(transactions, prices, names_to_group):
#     end = 0
#     start = 0
#     for name in names_to_group:
#         if name in transactions:
#             closed_transactions = [t for t in transactions[name] if t[IS_CLOSED_KEY]]
#             for match_id in range(len(closed_transactions) // 2):
#                 match_transactions = [t for t in closed_transactions if t[MATCH_ID_KEY] == match_id]
#                 assert len(match_transactions) == 2, f'There should be 2 transaction with match id: {match_id}'
#                 buy_t = [t for t in match_transactions if t[TYPE_KEY] != SELL_VALUE][0]
#                 sell_t = [t for t in match_transactions if t[TYPE_KEY] == SELL_VALUE][0]
#                 end += sell_t[AMOUNT_KEY] * sell_t[PRICE_KEY]
#                 start += buy_t[AMOUNT_KEY] * buy_t[PRICE_KEY]
#             open_transactions = [t for t in transactions[name] if not t[IS_CLOSED_KEY]]
#             start += sum([t[AMOUNT_KEY] * t[PRICE_KEY] for t in open_transactions])
#             end += prices[name] * sum([t[AMOUNT_KEY] for t in open_transactions])
#     return end / start - 1

def _compute_total_bitcoin(transactions):
    return sum([t[AMOUNT_KEY] for t in transactions[BITCOIN_NAME] if not t[IS_CLOSED_KEY]])

def _compute_etf_bitcoin(transactions):
    bitcoin = 0
    for name in INVESTMENTS[ETF_CATEGORY]:
        if name in transactions:
            total_open_amount = sum([t[AMOUNT_KEY] for t in transactions[name] if not t[IS_CLOSED_KEY]])
            bitcoin += get_bitcoin_per_share(name) * total_open_amount
    return bitcoin

def _compute_bitcoin_cost_basis(transactions):
    return sum([r[AMOUNT_KEY] * r[PRICE_KEY] for r in transactions[BITCOIN_NAME]]) \
        / sum([r[AMOUNT_KEY] for r in transactions[BITCOIN_NAME]])

def _format_metric(metrics):
    metrics[TOTAL_CATEGORY] = sum(metrics.values())
    return [format_price(metrics[category]) for category in TOTAL_CATEGORIES]

def _format_perc(metrics):
    return [''] + [format_perc(metrics[category]) for category in INVESTMENTS]

def _build_formatted_prices(prices):
    formatted_prices = {name: format_full_price(prices[name]) for name in prices}
    formatted_prices[BITCOIN_NAME] = format_price(prices[BITCOIN_NAME])
    return formatted_prices

# TODO: Move this to a config
def get_bitcoin_per_share(name):
    if name == IBIT_NAME:
        return 0.000568
    if name == BITB_NAME:
        return 0.000545
    raise Exception(f'{name} not supported!')
