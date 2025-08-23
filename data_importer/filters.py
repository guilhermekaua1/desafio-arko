# data_importer/filters.py
import django_filters
from .models import State, Municipality, District, Company

class StateFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nome do Estado')

    class Meta:
        model = State
        fields = ['name', 'region']

class MunicipalityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nome do Município')

    class Meta:
        model = Municipality
        fields = ['name', 'state']

class DistrictFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nome do Distrito')

    class Meta:
        model = District
        fields = ['name', 'municipality']

class CompanyFilter(django_filters.FilterSet):
    razao_social = django_filters.CharFilter(lookup_expr='icontains', label='Razão Social')

    class Meta:
        model = Company
        fields = ['razao_social', 'porte_empresa']