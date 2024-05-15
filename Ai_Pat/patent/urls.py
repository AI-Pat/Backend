from django.urls import path
from .views import country_trend, ytd_trend, countrywise_trend

urlpatterns = [
    path('country_trend', country_trend),
    path('countrywise_trend', countrywise_trend),
    path('ytd_trend', ytd_trend),
]