from ..models import BitcoinTransaction
from .http_client import HTTPClient
from .utils import format_perc, format_price


def build_context():
    bitcoin_price = HTTPClient.get_bitcoin_price()
    mstr_price = HTTPClient.get_cnbc_quote('MSTR')
    ibit_price = HTTPClient.get_cnbc_quote('IBIT')
    bitb_price = HTTPClient.get_cnbc_quote('BITB')
    bitcoin_transactions = BitcoinTransaction.objects.values()
    total_bitcoin = float(sum([r['bitcoin'] for r in bitcoin_transactions]))
    bitcoin_assets = bitcoin_price * total_bitcoin
    etf_assets = 0
    mstr_assets = 0
    total_assets = bitcoin_assets + etf_assets + mstr_assets
    bitcoin_cost_basis = float(sum([r['price'] * r['bitcoin'] for r in bitcoin_transactions])) / total_bitcoin
    etf_cost_basis = 1
    mstr_cost_basis = 1
    bitcoin_perc = bitcoin_assets / total_assets
    etf_perc = etf_assets / total_assets
    mstr_perc = mstr_assets / total_assets
    total_cost_basis = bitcoin_cost_basis * bitcoin_perc + etf_cost_basis * etf_perc + mstr_cost_basis * mstr_perc 
    return {
        'total_assets': format_price(total_assets),
        'bitcoin_assets': format_price(bitcoin_assets),
        'total_cost_basis': format_price(total_cost_basis),
        'bitcoin_cost_basis': format_price(bitcoin_cost_basis),
        'total_roi': format_perc(total_assets / total_cost_basis - 1),
        'bitcoin_roi': format_perc(bitcoin_assets / bitcoin_cost_basis - 1),
        'etf_roi': format_perc(etf_assets / etf_cost_basis - 1),
        'mstr_roi': format_perc(mstr_assets / mstr_cost_basis - 1),
        'total_profit': format_price(total_assets - total_cost_basis),
        'bitcoin_perc': format_perc(bitcoin_perc),
        'etf_perc': format_perc(etf_perc),
        'mstr_perc': format_perc(mstr_perc),
        'bitcoin_price': format_price(bitcoin_price),
        'mstr_price': format_price(mstr_price),
        'ibit_price': format_price(ibit_price),
        'bitb_price': format_price(bitb_price)
    }
