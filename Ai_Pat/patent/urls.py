from django.urls import path
from .views import country_trend, ytd_trend, countrywise_trend, countrywise_trend_all, applicant_trend_by_country

urlpatterns = [
    path('country_trend', country_trend),
    path('countrywise_trend', countrywise_trend),
    path('countrywise_trend_all', countrywise_trend_all),
    path('ytd_trend', ytd_trend),
    path('applicant_trend_by_country', applicant_trend_by_country),
]