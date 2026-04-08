from rest_framework import serializers

from app_core.models import District, DistrictScore


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


class DistrictScoreSerializer(serializers.ModelSerializer):
    source_id = serializers.IntegerField(source="district.source_id", read_only=True)
    division_id = serializers.IntegerField(
        source="district.division_id", read_only=True
    )
    name = serializers.CharField(source="district.name", read_only=True)
    bn_name = serializers.CharField(source="district.bn_name", read_only=True)
    latitude = serializers.DecimalField(
        source="district.latitude",
        max_digits=10,
        decimal_places=7,
        read_only=True,
    )
    longitude = serializers.DecimalField(
        source="district.longitude",
        max_digits=10,
        decimal_places=7,
        read_only=True,
    )

    class Meta:
        model = DistrictScore
        fields = (
            "source_id",
            "division_id",
            "name",
            "bn_name",
            "latitude",
            "longitude",
            "avg_temp_2pm_7d",
            "avg_pm25_7d",
            "calculated_at",
        )
