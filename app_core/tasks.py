from __future__ import annotations

import logging
from datetime import datetime
import requests
from celery import shared_task
from django.db import transaction

from app_core.models import District, DistrictScore, DistrictForecast
from .utils import (
    _next_n_day_dates,
    _district_coordinates,
    _get_avg_temp_2pm_7d,
    _get_avg_pm25_7d,
    _get_hourly_temperature_by_date,
    _get_hourly_pm25_by_date,
)

logger = logging.getLogger(__name__)


@shared_task
def populate_district_scores():
    start_date, end_date = _next_n_day_dates(7)
    updated_count = 0
    districts = District.objects.all()
    for district in districts:
        latitude, longitude = _district_coordinates(district)
        try:
            avg_temp = _get_avg_temp_2pm_7d(
                latitude,
                longitude,
                start_date,
                end_date,
            )
            avg_pm25 = _get_avg_pm25_7d(
                latitude,
                longitude,
                start_date,
                end_date,
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
    start_date, end_date = _next_n_day_dates(5)
    updated_count = 0
    districts = District.objects.all()
    for district in districts:
        latitude, longitude = _district_coordinates(district)
        try:
            temp_by_date = _get_hourly_temperature_by_date(
                latitude,
                longitude,
                start_date,
                end_date,
            )
            pm25_by_date = _get_hourly_pm25_by_date(
                latitude,
                longitude,
                start_date,
                end_date,
            )

            available_dates = sorted(
                set(temp_by_date.keys()) & set(pm25_by_date.keys())
            )

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
