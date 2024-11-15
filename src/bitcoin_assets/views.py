from django.http import HttpResponse
from .models import Transaction

def index(request):
    return HttpResponse(Transaction.objects.get(id=2).name)
