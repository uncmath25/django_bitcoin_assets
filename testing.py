r = requests.get('https://swapi.dev/api/starships/9/')
r = requests.get('https://coinmarketcap.com/currencies/bitcoin/')

from bs4 import BeautifulSoup
import requests

r = requests.get('https://coinmarketcap.com/currencies/bitcoin/')
soup = BeautifulSoup(r.content, "html.parser")
results = soup.find(id="section-coin-overview")
soup.findAll('span', {'data-test': 'text-cdp-price-display'})

r = requests.get('https://coinmarketcap.com/currencies/bitcoin/')
soup = BeautifulSoup(r.content, "html.parser")
soup.findAll('span', {'data-test': 'text-cdp-price-display'})[0].text

# curl --location 'https://api.coindesk.com/v1/bpi/currentprice.json'

r = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
r.json()['bpi']['USD']['rate_float']


r = requests.get('https://www.google.com/search?q=mstr+stock')
soup = BeautifulSoup(r.content, "html.parser")
results = soup.find(id="search")
soup.findAll('div', {'data-attrid': 'Price'})
soup.findAll('span', {'jsname': 'vWLAgc'})

results = soup.find(id="before-appbar")


r = requests.get('https://www.tradingview.com/symbols/NASDAQ-MSTR/')
soup = BeautifulSoup(r.content, "html.parser")
results = soup.findAll('div', {'data-symbol': 'NASDAQ:MSTR'})

r = requests.get('https://www.cnbc.com/quotes/MSTR')
soup = BeautifulSoup(r.content, "html.parser")
soup.findAll('span', {'class': 'QuoteStrip-lastPrice'})[0].text
