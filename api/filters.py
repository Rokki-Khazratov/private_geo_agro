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

    # Новые фильтры для is_deleting и is_checked
    is_deleting = django_filters.BooleanFilter(field_name='is_deleting')
    is_checked = django_filters.BooleanFilter(field_name='is_checked')

    class Meta:
        model = Plantation
        fields = [
            'name', 'inn', 'region_name', 'district_id', 'plantation_type', 'fruit_id', 'fruit_name', 
            'min_area', 'max_area', 'is_deleting', 'is_checked'
        ]



class StatisticsFilter(django_filters.FilterSet):
    region = django_filters.CharFilter(field_name='district__region__name', lookup_expr='icontains')
    district = django_filters.NumberFilter(field_name='district__id')

    class Meta:
        model = Plantation
        fields = ['region', 'district']
