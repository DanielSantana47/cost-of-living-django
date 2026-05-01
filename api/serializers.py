from rest_framework import serializers
from .models import City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class CityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""
    class Meta:
        model = City
        fields = [
            'id', 'city', 'country', 'data_quality',
            'avg_net_salary', 'meal_inexpensive_restaurant',
            'apt_1br_city_center', 'gasoline_1l',
            'basic_utilities_85m2', 'internet_60mbps',
        ]


class CountryStatsSerializer(serializers.Serializer):
    country = serializers.CharField()
    city_count = serializers.IntegerField()
    avg_salary = serializers.FloatField()
    avg_rent_1br_center = serializers.FloatField()
    avg_meal = serializers.FloatField()
    avg_gasoline = serializers.FloatField()
    avg_utilities = serializers.FloatField()


class GlobalStatsSerializer(serializers.Serializer):
    total_cities = serializers.IntegerField()
    total_countries = serializers.IntegerField()
    global_avg_salary = serializers.FloatField()
    global_avg_rent_1br = serializers.FloatField()
    global_avg_meal = serializers.FloatField()
    most_expensive_city = serializers.CharField()
    cheapest_city = serializers.CharField()
    highest_salary_city = serializers.CharField()


class CategoryComparisonSerializer(serializers.Serializer):
    city = serializers.CharField()
    country = serializers.CharField()
    value = serializers.FloatField()
