import csv

from django.core.management.base import BaseCommand

from foodgram.constants import CSV_DATA_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из CSV'

    def handle(self, *args, **options):
        self.stdout.write('Импорт ингредиентов...')
        with open(CSV_DATA_DIR / 'ingredients.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                self.stdout.write(f'Создан ингредиент: {row[0]}')
        self.stdout.write(self.style.SUCCESS('Импорт ингредиентов завершён!'))
