from django.urls import path
from .views import StateListView, MunicipalityListView, DistrictListView, CompanyListView

app_name = 'data_importer'

urlpatterns = [
    path('states/', StateListView.as_view(), name='state_list'),
    path('municipalities/', MunicipalityListView.as_view(), name='municipality_list'),
    path('districts/', DistrictListView.as_view(), name='district_list'),
    path('companies/', CompanyListView.as_view(), name='company_list'),
]