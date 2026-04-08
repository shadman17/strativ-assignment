from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app_core.models import District, DistrictScore
from app_api.serializers import DistrictSerializer, DistrictScoreSerializer


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
        "district__source_id"
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
