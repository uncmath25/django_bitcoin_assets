from django.urls import path

from . import views


app_name = 'bitcoin_assets'

urlpatterns = [
    path('', views.index, name='index'),
]
