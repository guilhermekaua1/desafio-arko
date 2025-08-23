from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import State, Municipality, District, Company
from .filters import StateFilter, MunicipalityFilter, DistrictFilter, CompanyFilter

class StateListView(LoginRequiredMixin, ListView):
    model = State
    template_name = 'data_importer/state_list.html'
    context_object_name = 'states'
    paginate_by = 20 # Define quantos itens por página

    def get_queryset(self):
        # Otimiza a query para evitar N+1 ao aceder à região
        queryset = super().get_queryset().select_related('region')
        # Aplica o filtro aos dados
        self.filter = StateFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        # Envia o objeto de filtro para o template
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

class MunicipalityListView(LoginRequiredMixin, ListView):
    model = Municipality
    template_name = 'data_importer/municipality_list.html'
    context_object_name = 'municipalities'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('state')
        self.filter = MunicipalityFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

class DistrictListView(LoginRequiredMixin, ListView):
    model = District
    template_name = 'data_importer/district_list.html'
    context_object_name = 'districts'
    paginate_by = 50

    def get_queryset(self):
        # Otimização avançada: busca o município e o estado relacionado de uma só vez
        queryset = super().get_queryset().select_related('municipality__state')
        self.filter = DistrictFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'data_importer/company_list.html'
    context_object_name = 'companies'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = CompanyFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context