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
