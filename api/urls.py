from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cities', views.CityViewSet, basename='city')

urlpatterns = [
    path('', include(router.urls)),

    # Global KPIs
    path('stats/global/', views.GlobalStatsView.as_view(), name='global-stats'),

    # Per-country aggregated stats
    path('stats/countries/', views.CountryStatsView.as_view(), name='country-stats'),

    # Rankings
    path('rankings/', views.CategoryRankingView.as_view(), name='rankings'),

    # City comparison (side-by-side)
    path('compare/', views.CityComparisonView.as_view(), name='compare'),

    # Salary vs rent affordability
    path('salary-rent-ratio/', views.SalaryRentRatioView.as_view(), name='salary-rent-ratio'),

    # Full cost breakdown for a single city
    path('cities/<int:pk>/breakdown/', views.CostBreakdownView.as_view(), name='city-breakdown'),

    # Helper lists
    path('countries/', views.countries_list, name='countries-list'),
    path('metrics/', views.metrics_list, name='metrics-list'),
]
