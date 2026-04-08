from django.db import models


class District(models.Model):
    source_id = models.PositiveIntegerField(unique=True)
    division_id = models.PositiveIntegerField(db_index=True)
    name = models.CharField(max_length=255)
    bn_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    class Meta:
        ordering = ["source_id"]

    def __str__(self):
        return f"{self.name} ({self.bn_name})"


class DistrictScore(models.Model):
    district = models.OneToOneField(
        District,
        on_delete=models.CASCADE,
        related_name="travel_score",
    )
    avg_temp_2pm_7d = models.FloatField()
    avg_pm25_7d = models.FloatField()
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["avg_temp_2pm_7d", "avg_pm25_7d", "district__source_id"]

    def __str__(self):
        return (
            f"{self.district.name}: temp={self.avg_temp_2pm_7d}, "
            f"pm25={self.avg_pm25_7d}"
        )
