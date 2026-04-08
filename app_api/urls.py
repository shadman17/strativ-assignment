from django.urls import path

from app_api.views import district_view, top_10_districts_view

urlpatterns = [
    path("api/v1/districts/", district_view, name="district-list"),
    path(
        "api/v1/districts/top-10-districts/",
        top_10_districts_view,
        name="top-10-districts",
    ),
]
