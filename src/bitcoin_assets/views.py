from django.http import HttpResponse
from django.shortcuts import render

from .service.processor import build_context


def index(request):
    return(render(request, 'index.html', build_context()))
