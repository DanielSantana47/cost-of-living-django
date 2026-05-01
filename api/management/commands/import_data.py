"""
Management command to import the cost-of-living CSV into the database.

Usage:
    python manage.py import_data
    python manage.py import_data --csv path/to/other.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from api.models import City

# Column mapping: CSV column name → model field name
COLUMN_MAP = {
    'x1':  'meal_inexpensive_restaurant',
    'x2':  'meal_for_two_mid_range',
    'x3':  'mcmeal_at_mcdonalds',
    'x4':  'domestic_beer_restaurant',
    'x5':  'imported_beer_restaurant',
    'x6':  'cappuccino',
    'x7':  'coke_pepsi',
    'x8':  'water_restaurant',
    'x9':  'milk_1l',
    'x10': 'bread_500g',
    'x11': 'rice_1kg',
    'x12': 'eggs_12',
    'x13': 'local_cheese_1kg',
    'x14': 'chicken_1kg',
    'x15': 'beef_1kg',
    'x16': 'apples_1kg',
    'x17': 'banana_1kg',
    'x18': 'oranges_1kg',
    'x19': 'tomato_1kg',
    'x20': 'potato_1kg',
    'x21': 'onion_1kg',
    'x22': 'lettuce',
    'x23': 'water_1_5l_market',
    'x24': 'wine_mid_range',
    'x25': 'domestic_beer_market',
    'x26': 'imported_beer_market',
    'x27': 'cigarettes_20pack',
    'x28': 'one_way_ticket',
    'x29': 'monthly_pass',
    'x30': 'taxi_start',
    'x31': 'taxi_1km',
    'x32': 'taxi_1hr_wait',
    'x33': 'gasoline_1l',
    'x34': 'volkswagen_golf',
    'x35': 'toyota_corolla',
    'x36': 'basic_utilities_85m2',
    'x37': 'mobile_monthly',
    'x38': 'internet_60mbps',
    'x39': 'fitness_club_monthly',
    'x40': 'tennis_court_1hr',
    'x41': 'cinema_ticket',
    'x42': 'preschool_monthly',
    'x43': 'intl_primary_school_annual',
    'x44': 'jeans_levis',
    'x45': 'summer_dress',
    'x46': 'nike_running_shoes',
    'x47': 'mens_leather_shoes',
    'x48': 'apt_1br_city_center',
    'x49': 'apt_1br_outside_center',
    'x50': 'apt_3br_city_center',
    'x51': 'apt_3br_outside_center',
    'x52': 'avg_net_salary',
    'x53': 'mortgage_rate',
    'x54': 'price_per_sqm_city_center',
    'x55': 'price_per_sqm_outside_center',
}


def parse_float(value):
    """Return float or None for empty/invalid values."""
    try:
        f = float(value)
        return f if f > 0 else None
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = 'Import cost-of-living CSV data into the database'

    def add_arguments(self, parser):
        default_csv = os.path.join(
            os.path.dirname(__file__), '..', '..', 'cost-of-living.csv'
        )
        parser.add_argument(
            '--csv',
            default=os.path.abspath(default_csv),
            help='Path to the CSV file (default: api/cost-of-living.csv)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        csv_path = options['csv']

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        if options['clear']:
            count, _ = City.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing records.'))

        self.stdout.write(f'Importing from {csv_path} ...')

        cities = []
        errors = 0
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    kwargs = {
                        'city': row['city'].strip(),
                        'country': row['country'].strip(),
                        'data_quality': parse_float(row.get('data_quality')),
                    }
                    for csv_col, model_field in COLUMN_MAP.items():
                        kwargs[model_field] = parse_float(row.get(csv_col))

                    cities.append(City(**kwargs))

                    # Bulk insert every 500 rows for performance
                    if len(cities) >= 500:
                        City.objects.bulk_create(cities, ignore_conflicts=True)
                        self.stdout.write(f'  Inserted batch up to row {i + 1}')
                        cities = []

                except Exception as e:
                    errors += 1
                    self.stderr.write(f'  Row {i + 1} error: {e}')

        if cities:
            City.objects.bulk_create(cities, ignore_conflicts=True)

        total = City.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Done! {total} cities in DB. Errors: {errors}'
        ))
