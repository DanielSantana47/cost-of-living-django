from django.db import models


class City(models.Model):
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    data_quality = models.FloatField(null=True, blank=True)

    # -- Food & Groceries (USD) --
    meal_inexpensive_restaurant = models.FloatField(null=True, blank=True)       # x1
    meal_for_two_mid_range = models.FloatField(null=True, blank=True)            # x2
    mcmeal_at_mcdonalds = models.FloatField(null=True, blank=True)              # x3
    domestic_beer_restaurant = models.FloatField(null=True, blank=True)         # x4
    imported_beer_restaurant = models.FloatField(null=True, blank=True)         # x5
    cappuccino = models.FloatField(null=True, blank=True)                        # x6
    coke_pepsi = models.FloatField(null=True, blank=True)                        # x7
    water_restaurant = models.FloatField(null=True, blank=True)                  # x8

    # -- Markets --
    milk_1l = models.FloatField(null=True, blank=True)                           # x9
    bread_500g = models.FloatField(null=True, blank=True)                        # x10
    rice_1kg = models.FloatField(null=True, blank=True)                          # x11
    eggs_12 = models.FloatField(null=True, blank=True)                           # x12
    local_cheese_1kg = models.FloatField(null=True, blank=True)                  # x13
    chicken_1kg = models.FloatField(null=True, blank=True)                       # x14
    beef_1kg = models.FloatField(null=True, blank=True)                          # x15
    apples_1kg = models.FloatField(null=True, blank=True)                        # x16
    banana_1kg = models.FloatField(null=True, blank=True)                        # x17
    oranges_1kg = models.FloatField(null=True, blank=True)                       # x18
    tomato_1kg = models.FloatField(null=True, blank=True)                        # x19
    potato_1kg = models.FloatField(null=True, blank=True)                        # x20
    onion_1kg = models.FloatField(null=True, blank=True)                         # x21
    lettuce = models.FloatField(null=True, blank=True)                           # x22
    water_1_5l_market = models.FloatField(null=True, blank=True)                 # x23
    wine_mid_range = models.FloatField(null=True, blank=True)                    # x24
    domestic_beer_market = models.FloatField(null=True, blank=True)              # x25
    imported_beer_market = models.FloatField(null=True, blank=True)              # x26
    cigarettes_20pack = models.FloatField(null=True, blank=True)                 # x27
    
    # -- Transport --
    one_way_ticket = models.FloatField(null=True, blank=True)                    # x28
    monthly_pass = models.FloatField(null=True, blank=True)                      # x29
    taxi_start = models.FloatField(null=True, blank=True)                        # x30
    taxi_1km = models.FloatField(null=True, blank=True)                          # x31
    taxi_1hr_wait = models.FloatField(null=True, blank=True)                     # x32
    gasoline_1l = models.FloatField(null=True, blank=True)                       # x33
    volkswagen_golf = models.FloatField(null=True, blank=True)                   # x34
    toyota_corolla = models.FloatField(null=True, blank=True)                    # x35

    # -- Utilities --
    basic_utilities_85m2 = models.FloatField(null=True, blank=True)              # x36
    mobile_monthly = models.FloatField(null=True, blank=True)                    # x37
    internet_60mbps = models.FloatField(null=True, blank=True)                   # x38

    # -- Sports & Leisure --
    fitness_club_monthly = models.FloatField(null=True, blank=True)              # x39
    tennis_court_1hr = models.FloatField(null=True, blank=True)                  # x40
    cinema_ticket = models.FloatField(null=True, blank=True)                     # x41

    # -- Childcare & Education --
    preschool_monthly = models.FloatField(null=True, blank=True)                 # x42
    intl_primary_school_annual = models.FloatField(null=True, blank=True)        # x43

    # -- Clothing --
    jeans_levis = models.FloatField(null=True, blank=True)                       # x44
    summer_dress = models.FloatField(null=True, blank=True)                      # x45
    nike_running_shoes = models.FloatField(null=True, blank=True)                # x46
    mens_leather_shoes = models.FloatField(null=True, blank=True)                # x47

    # -- Rent --
    apt_1br_city_center = models.FloatField(null=True, blank=True)               # x48
    apt_1br_outside_center = models.FloatField(null=True, blank=True)            # x49
    apt_3br_city_center = models.FloatField(null=True, blank=True)               # x50
    apt_3br_outside_center = models.FloatField(null=True, blank=True)            # x51

    # -- Salary & Buy Price --
    avg_net_salary = models.FloatField(null=True, blank=True)                    # x52
    mortgage_rate = models.FloatField(null=True, blank=True)                     # x53
    price_per_sqm_city_center = models.FloatField(null=True, blank=True)         # x54
    price_per_sqm_outside_center = models.FloatField(null=True, blank=True)      # x55

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['country', 'city']

    def __str__(self):
        return f"{self.city}, {self.country}"
