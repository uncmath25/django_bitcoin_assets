from django.core.management.base import BaseCommand
from bitcoin_assets.models import Asset


class Command(BaseCommand):
    help = 'Adds an asset to the database'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        item = Asset(
            name=options['name'])
        item.save()
        self.stdout.write(self.style.SUCCESS('Asset added successfully!'))
