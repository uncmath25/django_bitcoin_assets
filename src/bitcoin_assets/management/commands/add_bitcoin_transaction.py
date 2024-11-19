from django.core.management.base import BaseCommand
from bitcoin_assets.models import BitcoinTransaction


class Command(BaseCommand):
    help = 'Adds a transaction to the database'

    def add_arguments(self, parser):
        parser.add_argument('date', type=str)
        parser.add_argument('price', type=float)
        parser.add_argument('bitcoin', type=float)
        parser.add_argument('cost', type=float)

    def handle(self, *args, **options):
        item = BitcoinTransaction(
            date=options['date'],
            price=options['price'],
            bitcoin=options['bitcoin'],
            cost=options['cost'])
        item.save()
        self.stdout.write(self.style.SUCCESS('BitcoinTransaction added successfully!'))
