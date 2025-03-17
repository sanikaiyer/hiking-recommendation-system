import csv
from django.core.management.base import BaseCommand
from trails.models import Trail

class Command(BaseCommand):
    help = 'Load trails from CSV file'

    def handle(self, *args, **options):
        with open('hiking_trails.csv', mode='r') as file:
            reader = csv.DictReader(file, skipinitialspace=True)
            for row in reader:
                row = {key.strip(): value for key, value in row.items()}  # Clean fieldnames
                print(row)  # Debug print
                Trail.objects.create(
                    name=row['Name'],
                    location=row['Location'],
                    difficulty=row['Difficulty'],
                    distance=float(row['Distance (miles)']),
                    elevation_gain=float(row['Elevation Gain (feet)']),
                    rating=float(row['Rating']),
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded trails from CSV'))
