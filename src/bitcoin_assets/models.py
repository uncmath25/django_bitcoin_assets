from django.db import models


class BitcoinTransaction(models.Model):
    date = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bitcoin = models.DecimalField(max_digits=10, decimal_places=8)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    # class Meta:
    #     db_table = 'transaction'
