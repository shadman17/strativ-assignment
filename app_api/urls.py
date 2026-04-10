from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from app_api.views import (
    district_view,
    top_10_districts_view,
    travel_recommendation_view,
)

urlpatterns = [
    path("api/v1/auth/token/", obtain_auth_token, name="api-token-auth"),
    path("api/v1/districts/", district_view, name="district-list"),
    path(
        "api/v1/districts/top-10-districts/",
        top_10_districts_view,
        name="top-10-districts",
    ),
    path(
        "api/v1/travel/recommendation/",
        travel_recommendation_view,
        name="travel-recommendation",
    ),
]
