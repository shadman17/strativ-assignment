from rest_framework import serializers

from app_core.models import District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = (
            "source_id",
            "division_id",
            "name",
            "bn_name",
            "latitude",
            "longitude",
        )
