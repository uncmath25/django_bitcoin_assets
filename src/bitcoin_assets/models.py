from django.db import models
from enum import Enum


class Asset(models.Model):
    name = models.CharField(max_length=32)
    class Meta:
        db_table = 'asset'

class Transaction(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    is_sell = models.IntegerField()
    date = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=16, decimal_places=8)
    fee = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        db_table = 'transaction'

class Price(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        db_table = 'price'
