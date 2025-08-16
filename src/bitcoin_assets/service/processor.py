from ..models import Asset, Price, Transaction
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
    STOCKS_CATEGORY: ['MSTR', 'MTPLF', 'TSWCF', 'CINGF', 'STRC'],
    OPTIONS_CATEGORY: ['IBIT_CALL_Jan_16_26_75', 'IBIT_CALL_Jan_16_26_100']
}
TOTAL_CATEGORIES = [TOTAL_CATEGORY] + list(INVESTMENTS.keys())

ASSET_ID_KEY = 'id'
ASSET_NAME_KEY = 'name'
ASSET_KEY = 'asset_id'
IS_SELL_KEY = 'is_sell'
PRICE_KEY = 'price'
AMOUNT_KEY = 'amount'
FEE_KEY = 'fee'

IS_CLOSED_KEY = 'is_closed'
MATCH_ID_KEY = 'match_id'

# Assume that all sell transaction actually match 1 buy transaction
# Is a valid reduction, as all "buy = sell + buy (at sell price)"


def build_context():
    transactions = _clean_transactions(_get_raw_transactions())
    prices = _get_prices(transactions)
    _save_prices(prices)
    return _build_context_data(transactions, prices)

def _get_raw_transactions():
    asset_names = _get_asset_names()
    transactions = {}
    for r in Transaction.objects.values():
        d = {}
        d[PRICE_KEY] = float(r[PRICE_KEY])
        d[AMOUNT_KEY] = float(r[AMOUNT_KEY])
        d[FEE_KEY] = float(r[FEE_KEY])
        d[IS_SELL_KEY] = bool(r[IS_SELL_KEY])
        asset_id = int(r[ASSET_KEY])
        asset_name = asset_names[asset_id]
        if asset_name not in transactions:
            transactions[asset_name] = [d]
        else:
            transactions[asset_name].append(d)
    return transactions

def _get_asset_names():
    assets = {}
    for r in Asset.objects.values():
        id = int(r[ASSET_ID_KEY])
        name = str(r[ASSET_NAME_KEY])
        assets[id] = name
    return assets

def _clean_transactions(raw_transactions):
    transactions = {}
    for name in raw_transactions:
        sale_transactions = [t for t in raw_transactions[name] if t[IS_SELL_KEY]]
        transactions[name] = []
        match_id = 0
        for transaction in raw_transactions[name]:
            if not transaction[IS_SELL_KEY]:
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
    transaction[IS_SELL_KEY] = raw_transaction[IS_SELL_KEY]
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
    profit_percs = {c: current_balances[c] / (current_cost_bases[c] - realized_gains[c]) - 1 if current_balances[c] > 0 else 0 for c in INVESTMENTS}
    profit_percs[TOTAL_CATEGORY] = sum(current_balances.values()) / ( sum(current_cost_bases.values()) - sum(realized_gains.values()) ) - 1
    allocations = {c: current_balances[c] / sum(current_balances.values()) for c in INVESTMENTS}
    total_bitcoin = _compute_total_bitcoin(transactions)
    return {
        'categories': TOTAL_CATEGORIES,
        'current_cost_bases': _format_metric(current_cost_bases),
        'current_balances': _format_metric(current_balances),
        'unrealized_gains': _format_metric(unrealized_gains),
        'realized_gains': _format_metric(realized_gains),
        'profits': _format_metric(profits),
        'profit_percs': _format_perc(profit_percs, include_total=True),
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
                buy_t = [t for t in match_transactions if not t[IS_SELL_KEY]][0]
                sell_t = [t for t in match_transactions if t[IS_SELL_KEY]][0]
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
#                 buy_t = [t for t in match_transactions if not t[IS_SELL_KEY]][0]
#                 sell_t = [t for t in match_transactions if t[IS_SELL_KEY]][0]
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

def _format_perc(metrics, include_total=False):
    if include_total:
        return [format_perc(metrics[TOTAL_CATEGORY])] + [format_perc(metrics[category]) for category in INVESTMENTS]
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


def _get_historical_prices():
    prices = {}
    DATE_KEY = 'date'
    for r in Price.objects.values():
        name = str(r[NAME_KEY])
        price = float(r[PRICE_KEY])
        date = str(r[DATE_KEY])
        if date not in prices:
            prices[date] = {name: price}
        else:
            prices[date][name] = price
    return prices

def _save_prices(prices):
    current_date = _get_current_date()
    existing_prices = Price.objects.filter(date=current_date)
    if len(existing_prices) > 0:
        for r in existing_prices:
            r.price = prices[r.asset.name]
            r.save()
    else:
        for asset_name in prices:
            asset = Asset.objects.get(name=asset_name)
            Price(asset=asset, date=current_date, price=prices[asset_name]).save()

def _get_current_date():
    from datetime import datetime
    return datetime.today().strftime('%Y-%m-%d')
