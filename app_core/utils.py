from datetime import datetime, timedelta, timezone
import requests

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
REQUEST_TIMEOUT_SECONDS = 10


def _next_n_day_dates(days):
    utc_plus_6 = timezone(timedelta(hours=6))
    today = datetime.now(utc_plus_6).date()
    end_date = today + timedelta(days=days - 1)
    return today.isoformat(), end_date.isoformat()


def _district_coordinates(district):
    return float(district.latitude), float(district.longitude)


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


def _get_avg_pm25_7d(latitude, longitude, start_date, end_date):
    response = requests.get(
        AIR_QUALITY_API_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "pm2_5",
            "timezone": "Asia/Dhaka",
            "start_date": start_date,
            "end_date": end_date,
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

    response.raise_for_status()
    payload = response.json().get("hourly", {})
    date_to_temp = {}
    for ts, temp in zip(
        payload.get("time", []),
        payload.get("temperature_2m", []),
    ):
        if ts.endswith("14:00") and temp is not None:
            date_to_temp[ts[:10]] = temp

    return date_to_temp


def _get_hourly_pm25_by_date(latitude, longitude, start_date, end_date):
    response = requests.get(
        AIR_QUALITY_API_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "pm2_5",
            "timezone": "Asia/Dhaka",
            "start_date": start_date,
            "end_date": end_date,
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
