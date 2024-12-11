from bs4 import BeautifulSoup
import os
import requests


class HTTPClient():
    ''' Exposes HTTP client methods '''

    @staticmethod
    def get_cnbc_quote(stock_name):
        r = requests.get(f'https://www.cnbc.com/quotes/{stock_name}')
        soup = BeautifulSoup(r.content, "html.parser")
        raw_price = soup.findAll('span', {'class': 'QuoteStrip-lastPrice'})[0].text
        return(float(raw_price.replace(',', '')))
    
    @staticmethod
    def get_bitcoin_price():
        # r = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        # return r.json()['bpi']['USD']['rate_float']
        # r = requests.get('https://coinmarketcap.com/currencies/bitcoin/')
        # soup = BeautifulSoup(r.content, "html.parser")
        # return soup.findAll('span', {'data-test': 'text-cdp-price-display'})[0].text
        return HTTPClient.get_cnbc_quote('BTC.CM=')
    
    @staticmethod
    def get_option_price(option_name):
        # Temporary hack as option prices can not be scraped
        return float(os.environ[option_name + '_PRICE'])
