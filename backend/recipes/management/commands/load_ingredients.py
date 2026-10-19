"""Management command that loads ingredients from a CSV file."""

import csv

from django.core.management.base import BaseCommand

from foodgram.constants import CSV_DATA_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    """Import ingredients from ``data/ingredients.csv``.

    Each CSV row contains an ingredient name and its measurement unit.
    Existing ingredients are skipped, so the command is safe to re-run.
    """

    help = 'Load ingredients from data/ingredients.csv'

    def handle(self, *args, **options):
        self.stdout.write('Loading ingredients...')
        with open(CSV_DATA_DIR / 'ingredients.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                self.stdout.write(f'Added ingredient: {row[0]}')
        self.stdout.write(self.style.SUCCESS('Ingredients loaded.'))
