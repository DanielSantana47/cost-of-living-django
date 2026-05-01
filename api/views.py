from django.db.models import Avg, Count, Max, Min, Q
from rest_framework import viewsets, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import City
from .serializers import (
    CitySerializer, CityListSerializer,
    CountryStatsSerializer, GlobalStatsSerializer,
)


# ── City ViewSet ─────────────────────────────────────────────────────────────

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['city', 'country']
    ordering_fields = '__all__'
    ordering = ['country', 'city']

    def get_serializer_class(self):
        if self.action == 'list':
            return CityListSerializer
        return CitySerializer

    def get_queryset(self):
        qs = City.objects.all()
        country = self.request.query_params.get('country')
        if country:
            qs = qs.filter(country__iexact=country)
        return qs


# ── Global Stats ──────────────────────────────────────────────────────────────

class GlobalStatsView(APIView):

    def get(self, request):
        qs = City.objects.all()

        total_cities = qs.count()
        total_countries = qs.values('country').distinct().count()

        agg = qs.aggregate(
            avg_salary=Avg('avg_net_salary'),
            avg_rent=Avg('apt_1br_city_center'),
            avg_meal=Avg('meal_inexpensive_restaurant'),
        )

        # Most expensive city by rent
        most_expensive = (
            qs.exclude(apt_1br_city_center__isnull=True)
            .order_by('-apt_1br_city_center')
            .values('city', 'country')
            .first()
        )
        cheapest = (
            qs.exclude(apt_1br_city_center__isnull=True)
            .order_by('apt_1br_city_center')
            .values('city', 'country')
            .first()
        )
        highest_salary = (
            qs.exclude(avg_net_salary__isnull=True)
            .order_by('-avg_net_salary')
            .values('city', 'country')
            .first()
        )

        data = {
            'total_cities': total_cities,
            'total_countries': total_countries,
            'global_avg_salary': round(agg['avg_salary'] or 0, 2),
            'global_avg_rent_1br': round(agg['avg_rent'] or 0, 2),
            'global_avg_meal': round(agg['avg_meal'] or 0, 2),
            'most_expensive_city': f"{most_expensive['city']}, {most_expensive['country']}" if most_expensive else '-',
            'cheapest_city': f"{cheapest['city']}, {cheapest['country']}" if cheapest else '-',
            'highest_salary_city': f"{highest_salary['city']}, {highest_salary['country']}" if highest_salary else '-',
        }
        serializer = GlobalStatsSerializer(data)
        return Response(serializer.data)


# ── Country Stats ─────────────────────────────────────────────────────────────

class CountryStatsView(APIView):

    def get(self, request):
        country_filter = request.query_params.get('country')
        limit = request.query_params.get('limit')
        order_by = request.query_params.get('order_by', '-avg_salary')

        qs = City.objects.values('country').annotate(
            city_count=Count('id'),
            avg_salary=Avg('avg_net_salary'),
            avg_rent_1br_center=Avg('apt_1br_city_center'),
            avg_meal=Avg('meal_inexpensive_restaurant'),
            avg_gasoline=Avg('gasoline_1l'),
            avg_utilities=Avg('basic_utilities_85m2'),
        )

        if country_filter:
            qs = qs.filter(country__icontains=country_filter)

        allowed_order = [
            'country', '-country', 'avg_salary', '-avg_salary',
            'avg_rent_1br_center', '-avg_rent_1br_center',
            'avg_meal', '-avg_meal', 'city_count', '-city_count',
        ]

        if order_by not in allowed_order:
            order_by = '-avg_salary'

        qs = qs.order_by(order_by)

        if limit:
            qs = qs[:int(limit)]

        results = [
            {
                'country': row['country'],
                'city_count': row['city_count'],
                'avg_salary': round(row['avg_salary'] or 0, 2),
                'avg_rent_1br_center': round(row['avg_rent_1br_center'] or 0, 2),
                'avg_meal': round(row['avg_meal'] or 0, 2),
                'avg_gasoline': round(row['avg_gasoline'] or 0, 2),
                'avg_utilities': round(row['avg_utilities'] or 0, 2),
            }
            for row in qs
        ]

        serializer = CountryStatsSerializer(results, many=True)
        return Response(serializer.data)


# ── Category Rankings ─────────────────────────────────────────────────────────

RANKABLE_FIELDS = {
    # Food
    'meal_inexpensive_restaurant': 'Meal (Inexpensive Restaurant)',
    'meal_for_two_mid_range': 'Meal for Two (Mid-Range)',
    'mcmeal_at_mcdonalds': 'McMeal at McDonald\'s',
    'cappuccino': 'Cappuccino',
    'milk_1l': 'Milk (1L)',
    'bread_500g': 'Bread (500g)',
    'rice_1kg': 'Rice (1kg)',
    'eggs_12': 'Eggs (12)',
    'chicken_1kg': 'Chicken (1kg)',
    'beef_1kg': 'Beef (1kg)',
    # Transport
    'one_way_ticket': 'Public Transport (One Way)',
    'monthly_pass': 'Monthly Transport Pass',
    'taxi_1km': 'Taxi (1km)',
    'gasoline_1l': 'Gasoline (1L)',
    'volkswagen_golf': 'Volkswagen Golf (new)',
    # Housing
    'apt_1br_city_center': 'Apt 1BR - City Center (monthly)',
    'apt_1br_outside_center': 'Apt 1BR - Outside Center (monthly)',
    'apt_3br_city_center': 'Apt 3BR - City Center (monthly)',
    'price_per_sqm_city_center': 'Price/m² - City Center (buy)',
    'price_per_sqm_outside_center': 'Price/m² - Outside Center (buy)',
    # Utilities
    'basic_utilities_85m2': 'Basic Utilities (85m²)',
    'internet_60mbps': 'Internet (60 Mbps)',
    'mobile_monthly': 'Mobile (Monthly)',
    # Salary
    'avg_net_salary': 'Average Net Salary',
}


class CategoryRankingView(APIView):

    MAX_LIMIT = 50
    DEFAULT_LIMIT = 10

    def get(self, request):
        metric = request.query_params.get('metric', 'avg_net_salary')
        limit = int(request.query_params.get('limit', self.DEFAULT_LIMIT))
        order = request.query_params.get('order', 'desc')
        country = request.query_params.get('country')

        if metric not in RANKABLE_FIELDS:
            return Response(
                {'error': f'Invalid metric. Choose from: {list(RANKABLE_FIELDS.keys())}'},
                status=400,
            )

        limit = min(limit, self.MAX_LIMIT)

        qs = City.objects.exclude(**{f'{metric}__isnull': True})

        if country:
            qs = qs.filter(country__iexact=country)

        qs = qs.values('city', 'country').annotate(
            value=Max(metric)
        )

        direction = '-' if order == 'desc' else ''
        qs = qs.order_by(f'{direction}value')[:limit]

        results = [
            {
                'city': row['city'],
                'country': row['country'],
                'value': row['value'],
            }
            for row in qs
        ]

        return Response({
            'metric': metric,
            'metric_label': RANKABLE_FIELDS[metric],
            'order': order,
            'limit': limit,
            'results': results,
        })


# ── City Comparison ───────────────────────────────────────────────────────────

class CityComparisonView(APIView):

    MAX_CITIES = 5

    def get(self, request):
        cities_param = request.query_params.get('cities', '')
        city_names = [c.strip() for c in cities_param.split(',') if c.strip()]

        if not city_names:
            return Response({'error': 'Provide ?cities=City1,City2,...'}, status=400)

        if len(city_names) > self.MAX_CITIES:
            return Response(
                {'error': f'Maximum {self.MAX_CITIES} cities allowed.'},
                status=400
            )

        query = Q()
        for name in city_names:
            query |= Q(city__iexact=name)

        cities = City.objects.filter(query)

        results = CitySerializer(cities, many=True).data

        return Response({
            'cities': results,
            'available_metrics': RANKABLE_FIELDS,
        })


# ── Countries List ────────────────────────────────────────────────────────────

@api_view(['GET'])
def countries_list(request):
    countries = (
        City.objects.values_list('country', flat=True)
        .distinct()
        .order_by('country')
    )
    return Response(list(countries))


# ── Metrics List ──────────────────────────────────────────────────────────────

@api_view(['GET'])
def metrics_list(request):
    return Response(RANKABLE_FIELDS)


# ── Salary vs Rent ratio ──────────────────────────────────────────────────────

class SalaryRentRatioView(APIView):

    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        order = request.query_params.get('order', 'desc')
        country = request.query_params.get('country')

        qs = City.objects.exclude(
            avg_net_salary__isnull=True
        ).exclude(
            apt_1br_city_center__isnull=True
        ).exclude(
            apt_1br_city_center=0
        )

        if country:
            qs = qs.filter(country__iexact=country)

        cities = list(
            qs.values('city', 'country')
            .annotate(
                avg_net_salary=Avg('avg_net_salary'),
                apt_1br_city_center=Avg('apt_1br_city_center')
            )
        )

        # cálculo do ratio
        for c in cities:
            ratio = c['avg_net_salary'] / c['apt_1br_city_center']
            c['salary_rent_ratio'] = round(ratio, 2)

        reverse = order == 'desc'
        cities.sort(key=lambda x: x['salary_rent_ratio'], reverse=reverse)

        cities = cities[:limit]

        return Response({
            'description': 'Salary-to-rent ratio: higher = more affordable (salary covers more months of rent)',
            'order': order,
            'results': cities,
        })


class CostBreakdownView(APIView):

    def get(self, request, pk):
        try:
            city = City.objects.get(pk=pk)
        except City.DoesNotExist:
            return Response({'error': 'City not found'}, status=404)

        def safe(val):
            return round(val, 2) if val is not None else None

        breakdown = {
            'city': city.city,
            'country': city.country,
            'data_quality': city.data_quality,
            'categories': {
                'restaurants': {
                    'label': 'Restaurants',
                    'items': {
                        'Meal (Inexpensive)': safe(city.meal_inexpensive_restaurant),
                        'Meal for 2 (Mid-Range)': safe(city.meal_for_two_mid_range),
                        'McMeal': safe(city.mcmeal_at_mcdonalds),
                        'Domestic Beer': safe(city.domestic_beer_restaurant),
                        'Imported Beer': safe(city.imported_beer_restaurant),
                        'Cappuccino': safe(city.cappuccino),
                        'Coke/Pepsi': safe(city.coke_pepsi),
                        'Water': safe(city.water_restaurant),
                    },
                },
                'markets': {
                    'label': 'Markets',
                    'items': {
                        'Milk (1L)': safe(city.milk_1l),
                        'Bread (500g)': safe(city.bread_500g),
                        'Rice (1kg)': safe(city.rice_1kg),
                        'Eggs (12)': safe(city.eggs_12),
                        'Cheese (1kg)': safe(city.local_cheese_1kg),
                        'Chicken (1kg)': safe(city.chicken_1kg),
                        'Beef (1kg)': safe(city.beef_1kg),
                        'Apples (1kg)': safe(city.apples_1kg),
                        'Banana (1kg)': safe(city.banana_1kg),
                        'Oranges (1kg)': safe(city.oranges_1kg),
                        'Tomato (1kg)': safe(city.tomato_1kg),
                        'Potato (1kg)': safe(city.potato_1kg),
                        'Onion (1kg)': safe(city.onion_1kg),
                        'Lettuce': safe(city.lettuce),
                        'Water (1.5L)': safe(city.water_1_5l_market),
                        'Wine (mid-range)': safe(city.wine_mid_range),
                        'Domestic Beer (market)': safe(city.domestic_beer_market),
                        'Imported Beer (market)': safe(city.imported_beer_market),
                        'Cigarettes (20 pack)': safe(city.cigarettes_20pack),
                    },
                },
                'transport': {
                    'label': 'Transportation',
                    'items': {
                        'One-way Ticket': safe(city.one_way_ticket),
                        'Monthly Pass': safe(city.monthly_pass),
                        'Taxi Start': safe(city.taxi_start),
                        'Taxi (1km)': safe(city.taxi_1km),
                        'Taxi (1hr wait)': safe(city.taxi_1hr_wait),
                        'Gasoline (1L)': safe(city.gasoline_1l),
                        'VW Golf (new)': safe(city.volkswagen_golf),
                        'Toyota Corolla (new)': safe(city.toyota_corolla),
                    },
                },
                'utilities': {
                    'label': 'Utilities',
                    'items': {
                        'Basic Utilities (85m²)': safe(city.basic_utilities_85m2),
                        'Mobile (monthly)': safe(city.mobile_monthly),
                        'Internet (60Mbps)': safe(city.internet_60mbps),
                    },
                },
                'leisure': {
                    'label': 'Sports & Leisure',
                    'items': {
                        'Fitness Club (monthly)': safe(city.fitness_club_monthly),
                        'Tennis (1hr)': safe(city.tennis_court_1hr),
                        'Cinema Ticket': safe(city.cinema_ticket),
                    },
                },
                'childcare': {
                    'label': 'Childcare & Education',
                    'items': {
                        'Preschool (monthly)': safe(city.preschool_monthly),
                        'Intl Primary School (annual)': safe(city.intl_primary_school_annual),
                    },
                },
                'clothing': {
                    'label': 'Clothing',
                    'items': {
                        'Levi\'s Jeans': safe(city.jeans_levis),
                        'Summer Dress': safe(city.summer_dress),
                        'Nike Running Shoes': safe(city.nike_running_shoes),
                        'Leather Shoes': safe(city.mens_leather_shoes),
                    },
                },
                'rent': {
                    'label': 'Rent (monthly)',
                    'items': {
                        '1BR - City Center': safe(city.apt_1br_city_center),
                        '1BR - Outside Center': safe(city.apt_1br_outside_center),
                        '3BR - City Center': safe(city.apt_3br_city_center),
                        '3BR - Outside Center': safe(city.apt_3br_outside_center),
                    },
                },
                'buy': {
                    'label': 'Real Estate (buy)',
                    'items': {
                        'Price/m² - City Center': safe(city.price_per_sqm_city_center),
                        'Price/m² - Outside Center': safe(city.price_per_sqm_outside_center),
                        'Mortgage Rate (%)': safe(city.mortgage_rate),
                    },
                },
                'salary': {
                    'label': 'Salary',
                    'items': {
                        'Average Net Salary': safe(city.avg_net_salary),
                    },
                },
            },
        }

        return Response(breakdown)
