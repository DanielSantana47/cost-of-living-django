from django.contrib import admin
from .models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['city', 'country', 'avg_net_salary', 'apt_1br_city_center', 'data_quality']
    list_filter = ['country']
    search_fields = ['city', 'country']
    ordering = ['country', 'city']
