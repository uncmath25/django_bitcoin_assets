from django.db import models
from enum import Enum


class TransactionType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class Transaction(models.Model):
    name = models.CharField(max_length=16)
    type = models.CharField(max_length=4, choices=[(tag.name, tag.value) for tag in TransactionType])
    date = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=16, decimal_places=8)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        db_table = 'transaction'