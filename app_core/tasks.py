from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import requests
from celery import shared_task
from django.db import transaction

from app_core.models import District, DistrictScore

logger = logging.getLogger(__name__)

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
REQUEST_TIMEOUT_SECONDS = 10


def _next_7_day_dates():
    today = datetime.now(timezone.utc).date()
    end_date = today + timedelta(days=6)
    return today.isoformat(), end_date.isoformat()


def _average_for_hour(times, values, hour):
    selected_values = []
    for ts, value in zip(times, values):
        if ts.endswith(hour) and value is not None:
            selected_values.append(value)
    if not selected_values:
        return None

    return sum(selected_values) / len(selected_values)


def _get_avg_temp_2pm_7d(latitude, longitude, start_date, end_date):
    response = requests.get(
        WEATHER_API_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
            "timezone": "UTC",
            "start_date": start_date,
            "end_date": end_date,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json().get("hourly", {})
    return _average_for_hour(
        payload.get("time", []),
        payload.get("temperature_2m", []),
        "14:00",
    )


def _get_avg_pm25_7d(latitude, longitude):
    response = requests.get(
        AIR_QUALITY_API_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "pm2_5",
            "timezone": "UTC",
            "past_days": 7,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json().get("hourly", {})
    pm25_values = []
    for value in payload.get("pm2_5", []):
        if value is not None:
            pm25_values.append(value)
    if not pm25_values:
        return None
    return sum(pm25_values) / len(pm25_values)


@shared_task
def populate_district_scores():
    start_date, end_date = _next_7_day_dates()
    updated_count = 0

    for district in District.objects.all():
        try:
            avg_temp = _get_avg_temp_2pm_7d(
                float(district.latitude),
                float(district.longitude),
                start_date,
                end_date,
            )
            avg_pm25 = _get_avg_pm25_7d(
                float(district.latitude),
                float(district.longitude),
            )

            if avg_temp is None or avg_pm25 is None:
                logger.warning(
                    "Skipping district %s due to missing weather/air-quality values",
                    district.source_id,
                )
                continue

            with transaction.atomic():
                DistrictScore.objects.update_or_create(
                    district=district,
                    defaults={
                        "avg_temp_2pm_7d": avg_temp,
                        "avg_pm25_7d": avg_pm25,
                    },
                )
            updated_count += 1
        except Exception as exc:
            logger.exception(
                "Failed to populate score for district %s: %s",
                district.source_id,
                exc,
            )

    return f"Updated district scores for {updated_count} districts"
