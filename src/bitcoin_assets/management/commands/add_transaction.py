from django.core.management.base import BaseCommand
from bitcoin_assets.models import Transaction


class Command(BaseCommand):
    help = 'Adds a transaction to the database'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        item = Transaction(name=options['name'])
        item.save()
        self.stdout.write(self.style.SUCCESS('Transaction added successfully!'))
