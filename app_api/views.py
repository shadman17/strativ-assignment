from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


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
