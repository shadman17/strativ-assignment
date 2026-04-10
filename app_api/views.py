from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app_core.models import District, DistrictScore, DistrictForecast
from .serializers import (
    DistrictSerializer,
    DistrictScoreSerializer,
    TravelSerializer,
)
from .utils import get_nearest_district


@api_view(["GET"])
def district_view(request):
    """Return Districts"""
    districts = District.objects.all().order_by("source_id")
    serializer = DistrictSerializer(districts, many=True)

    return Response(
        {
            "message": "List of districts",
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def top_10_districts_view(request):
    """Return top 10 Districts"""
    top_districts = DistrictScore.objects.select_related("district").order_by(
        "avg_temp_2pm_7d", "avg_pm25_7d", "district__source_id"
    )[:10]
    print("top districts")
    print(top_districts)
    serializer = DistrictScoreSerializer(top_districts, many=True)

    return Response(
        {
            "message": "Top 10 districts.",
            "results": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def travel_recommendation_view(request):
    serializer = TravelSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    latitude = serializer.validated_data["latitude"]
    longitude = serializer.validated_data["longitude"]
    destination_district = serializer.validated_data["destination_district"]
    travel_date = serializer.validated_data["travel_date"]

    nearest_district = get_nearest_district(latitude, longitude)
    if nearest_district is None:
        return Response(
            {"detail": "No district data available."},
            status=status.HTTP_404_NOT_FOUND,
        )

    current_forecast = DistrictForecast.objects.filter(
        district=nearest_district,
        forecast_date=travel_date,
    ).first()
    destination_forecast = DistrictForecast.objects.filter(
        district=destination_district,
        forecast_date=travel_date,
    ).first()

    if not current_forecast or not destination_forecast:
        return Response(
            {
                "detail": "Forecast not available for one or both districts on the selected date."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    temp_diff = round(current_forecast.temp_2pm - destination_forecast.temp_2pm, 1)

    is_cooler = destination_forecast.temp_2pm < current_forecast.temp_2pm
    has_better_air = destination_forecast.pm25_2pm < current_forecast.pm25_2pm
    is_recommended = is_cooler and has_better_air
    reason = ""

    if is_recommended:
        reason += f"Your destination is {abs(temp_diff)}°C cooler and significantly better air quality. Enjoy your trip!"
    elif not is_cooler and not has_better_air:
        reason += (
            "Your destination is hotter and has worse air quality than your current "
            "location. It's better to stay where you are."
        )
    elif not is_cooler and has_better_air:
        reason += "Your destination is hotter than your current location but has better air quality."
    elif is_cooler and not has_better_air:
        reason += f"Your destination is {abs(temp_diff)}°C cooler but has worse air quality than your current location."

    return Response(
        {
            "recommendation": "Recommended" if is_recommended else "Not Recommended",
            "reason": reason,
            "selected_date": travel_date,
            "current_location": {
                "nearest_district": nearest_district.name,
                "temp_2pm": current_forecast.temp_2pm,
                "pm25_2pm": current_forecast.pm25_2pm,
            },
            "destination": {
                "district": destination_district.name,
                "temp_2pm": destination_forecast.temp_2pm,
                "pm25_2pm": destination_forecast.pm25_2pm,
            },
        },
        status=status.HTTP_200_OK,
    )
