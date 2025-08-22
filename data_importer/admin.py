from django.contrib import admin
from .models import Region, State, Municipality, District

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'acronym')
    search_fields = ('name', 'acronym')

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'acronym', 'region')
    search_fields = ('name', 'acronym')
    list_filter = ('region',)

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state')
    search_fields = ('name',)
    list_filter = ('state__region', 'state')

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'municipality', 'get_state')
    search_fields = ('name', 'municipality__name')
    list_filter = ('municipality__state__region', 'municipality__state')

    @admin.display(description='Estado', ordering='municipality__state')
    def get_state(self, obj):
        return obj.municipality.state.acronym
