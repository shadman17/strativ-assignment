from django.contrib import admin

from app_core.models import District, DistrictScore, DistrictForecast

admin.site.register(District)
admin.site.register(DistrictScore)
admin.site.register(DistrictForecast)
