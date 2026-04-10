from rest_framework import serializers
from datetime import date, timedelta
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


class TravelSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    destination_district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        source="destination_district",
    )
    travel_date = serializers.DateField()

    def validate_travel_date(self, value):
        today = date.today()
        if value < today:
            raise serializers.ValidationError("Travel date cannot be in the past.")
        if value > today + timedelta(days=30):
            raise serializers.ValidationError(
                "Travel date must be within the next 30 days."
            )
        return value
