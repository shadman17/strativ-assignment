from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app_core.models import District, DistrictForecast


class TravelRecommendationViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="test-user",
            password="pass1234",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.current_district = District.objects.create(
            source_id=1,
            division_id=10,
            name="Current",
            bn_name="বর্তমান",
            latitude=23.80,
            longitude=90.40,
        )
        self.destination_district = District.objects.create(
            source_id=2,
            division_id=10,
            name="Destination",
            bn_name="গন্তব্য",
            latitude=24.00,
            longitude=90.60,
        )

        self.url = reverse("travel-recommendation")
        self.travel_date = date.today() + timedelta(days=1)

    def _payload(self, destination_id=None):
        return {
            "latitude": 23.80,
            "longitude": 90.40,
            "destination_district_id": destination_id or self.destination_district.pk,
            "travel_date": self.travel_date.isoformat(),
        }

    def test_returns_not_recommended_when_source_and_destination_are_same(self):
        response = self.client.post(
            self.url,
            data=self._payload(destination_id=self.current_district.pk),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["recommendation"], "Not Recommended")
        self.assertIn("same district", response.data["reason"])

    def test_returns_404_when_forecast_data_missing(self):
        response = self.client.post(self.url, data=self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Forecast not available", response.data["detail"])

    def test_recommends_travel_when_destination_is_cooler_and_cleaner(self):
        DistrictForecast.objects.create(
            district=self.current_district,
            forecast_date=self.travel_date,
            temp_2pm=34.0,
            pm25_2pm=65.0,
        )
        DistrictForecast.objects.create(
            district=self.destination_district,
            forecast_date=self.travel_date,
            temp_2pm=31.5,
            pm25_2pm=40.0,
        )

        response = self.client.post(self.url, data=self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["recommendation"], "Recommended")
        self.assertIn("2.5°C cooler", response.data["reason"])
        self.assertIn("better air quality", response.data["reason"])
