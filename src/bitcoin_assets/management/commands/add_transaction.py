from django.core.management.base import BaseCommand
from bitcoin_assets.models import Transaction


class Command(BaseCommand):
    help = 'Adds a transaction to the database'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('type', type=str)
        parser.add_argument('date', type=str)
        parser.add_argument('price', type=float)
        parser.add_argument('amount', type=float)
        parser.add_argument('fee', type=float)

    def handle(self, *args, **options):
        item = Transaction(
            name=options['name'],
            type=options['type'],
            date=options['date'],
            price=options['price'],
            amount=options['amount'],
            fee=options['fee'])
        item.save()
        self.stdout.write(self.style.SUCCESS('Transaction added successfully!'))
