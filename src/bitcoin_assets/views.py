from django.http import HttpResponse
from django.shortcuts import render

from .http_client import HTTPClient
from .models import Transaction
from .utils import format_price


def index(request):
    # return HttpResponse(Transaction.objects.get(id=2).name)
    context = {
        'bitcoin_price': format_price(HTTPClient.get_bitcoin_price()),
        'mstr_price': format_price(HTTPClient.get_cnbc_quote('MSTR')),
        'ibit_price': format_price(HTTPClient.get_cnbc_quote('IBIT')),
        'bitb_price': format_price(HTTPClient.get_cnbc_quote('BITB'))
    }
    return(render(request, 'index.html', context))
