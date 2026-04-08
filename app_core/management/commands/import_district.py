from decimal import Decimal

import requests
from django.core.management.base import BaseCommand, CommandError

from app_core.models import District

DISTRICTS_SOURCE_URL = (
    "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/"
    "bd-districts.json"
)


class Command(BaseCommand):
    help = "Fetch Bangladesh district data from source and populate local database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=DISTRICTS_SOURCE_URL,
            help="Alternative source URL for district payload",
        )

    def handle(self, *args, **options):
        source_url = options["url"]

        try:
            response = requests.get(source_url, timeout=30)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise CommandError(f"Failed to fetch district data: {error}") from error
        except ValueError as error:
            raise CommandError(f"Invalid JSON response: {error}") from error

        districts = payload.get("districts", [])
        if not isinstance(districts, list):
            raise CommandError(
                "Invalid payload format. Expected `districts` to be a list."
            )

        created_count = 0
        updated_count = 0

        for district_data in districts:
            _, created = District.objects.update_or_create(
                source_id=int(district_data["id"]),
                defaults={
                    "division_id": int(district_data["division_id"]),
                    "name": district_data["name"],
                    "bn_name": district_data["bn_name"],
                    "latitude": Decimal(district_data["lat"]),
                    "longitude": Decimal(district_data["long"]),
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"District sync complete. Created: {created_count}, Updated: {updated_count}"
            )
        )
