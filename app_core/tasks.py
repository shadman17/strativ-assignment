from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import requests
from celery import shared_task
from django.db import transaction

from app_core.models import District, DistrictScore, DistrictForecast

logger = logging.getLogger(__name__)

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
REQUEST_TIMEOUT_SECONDS = 10


def _next_7_day_dates():
    utc_plus_6 = timezone(timedelta(hours=6))
    today = datetime.now(utc_plus_6).date()
    end_date = today + timedelta(days=6)
    return today.isoformat(), end_date.isoformat()


def _average_for_hour(times, values, hour):
    selected_values = []
    # print(times)

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
            "timezone": "Asia/Dhaka",
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
            "timezone": "Asia/Dhaka",
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


def _get_hourly_temperature_by_date(latitude, longitude, start_date, end_date):
    response = requests.get(
        WEATHER_API_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
            "timezone": "Asia/Dhaka",
            "start_date": start_date,
            "end_date": end_date,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    # print(response.json())
    response.raise_for_status()
    payload = response.json().get("hourly", {})
    # print(payload)
    date_to_temp = {}
    for ts, temp in zip(
        payload.get("time", []),
        payload.get("temperature_2m", []),
    ):
        if ts.endswith("14:00") and temp is not None:
            date_to_temp[ts[:10]] = temp

    return date_to_temp


def _get_hourly_pm25_by_date(latitude, longitude, forecast_days):
    response = requests.get(
        AIR_QUALITY_API_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "pm2_5",
            "timezone": "Asia/Dhaka",
            "forecast_days": forecast_days,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json().get("hourly", {})

    date_to_pm25 = {}
    for ts, pm25 in zip(
        payload.get("time", []),
        payload.get("pm2_5", []),
    ):
        if ts.endswith("14:00") and pm25 is not None:
            date_to_pm25[ts[:10]] = pm25

    return date_to_pm25


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


@shared_task
def populate_district_forecasts():
    start_date, end_date = _next_7_day_dates()
    forecast_days = (
        datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)
    ).days + 1
    updated_count = 0

    for district in District.objects.all():
        try:
            temp_by_date = _get_hourly_temperature_by_date(
                float(district.latitude),
                float(district.longitude),
                start_date,
                end_date,
            )
            pm25_by_date = _get_hourly_pm25_by_date(
                float(district.latitude),
                float(district.longitude),
                forecast_days,
            )
            # print(temp_by_date)
            # print(pm25_by_date)

            available_dates = sorted(
                set(temp_by_date.keys()) & set(pm25_by_date.keys())
            )

            # print(available_dates)
            if not available_dates:
                logger.warning(
                    "Skipping district %s due to missing forecast values",
                    district.source_id,
                )
                continue

            with transaction.atomic():
                for forecast_date in available_dates:
                    DistrictForecast.objects.update_or_create(
                        district=district,
                        forecast_date=forecast_date,
                        defaults={
                            "temp_2pm": temp_by_date[forecast_date],
                            "pm25_2pm": pm25_by_date[forecast_date],
                        },
                    )
                    updated_count += 1
        except Exception as exc:
            logger.exception(
                "Failed to populate forecasts for district %s: %s",
                district.source_id,
                exc,
            )

    return f"Updated district forecasts for {updated_count} district-date rows"
