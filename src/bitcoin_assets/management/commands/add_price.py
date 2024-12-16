from django.core.management.base import BaseCommand
from bitcoin_assets.models import Asset, Price


class Command(BaseCommand):
    help = 'Adds a price to the database'

    def add_arguments(self, parser):
        parser.add_argument('asset_id', type=int)
        parser.add_argument('date', type=str)
        parser.add_argument('price', type=float)

    def handle(self, *args, **options):
        item = Price(
            asset=Asset.objects.get(id=options['asset_id']),
            date=options['date'],
            price=options['price'])
        item.save()
        self.stdout.write(self.style.SUCCESS('Price added successfully!'))
