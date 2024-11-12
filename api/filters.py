import django_filters
from .models import Plantation

class PlantationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    inn = django_filters.NumberFilter()
    region_id = django_filters.NumberFilter(field_name='district__region__id')
    region_name = django_filters.CharFilter(field_name='district__region__name', lookup_expr='icontains')
    district_id = django_filters.NumberFilter(field_name='district__id')
    plantation_type = django_filters.NumberFilter()
    fruit_id = django_filters.NumberFilter(field_name='fruit_area__fruit__id')
    fruit_name = django_filters.CharFilter(field_name='fruit_area__fruit__name', lookup_expr='icontains')
    min_area = django_filters.NumberFilter(field_name='fruit_area__area', lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name='fruit_area__area', lookup_expr='lte')

    class Meta:
        model = Plantation
        fields = ['name', 'inn', 'region_id', 'region_name', 'district_id', 'plantation_type', 'fruit_id', 'fruit_name', 'min_area', 'max_area']
