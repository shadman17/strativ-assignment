from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app_core.models import District
from app_api.serializers import DistrictSerializer


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
    """Return Top 10 Districts"""
    return Response(
        {
            "message": "Top 10 districts endpoint scaffolded.",
            "results": [],
        },
        status=status.HTTP_200_OK,
    )
