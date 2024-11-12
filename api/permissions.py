from rest_framework import permissions
from api.models import *





class IsDistrictOwner(permissions.BasePermission):
    """
    Разрешение, которое проверяет, может ли пользователь видеть только те данные, которые принадлежат его округу.
    """

    def has_permission(self, request, view):
        # Проверяем, что пользователь аутентифицирован
        if not request.user.is_authenticated:
            return False
        
        # Проверяем округ пользователя
        district_ids = request.user.districts.values_list('id', flat=True)
        
        if view.action == 'list':
            # Для списка фильтруем только плантации в доступных округах
            return view.queryset.filter(district__id__in=district_ids).exists()

        # Для детализированных представлений проверяем округ текущей плантации
        return view.get_object().district.id in district_ids







class IsDistrictOwnerForCoordinates(permissions.BasePermission):
    """
    Разрешение, которое проверяет, имеет ли пользователь доступ к координатам плантации в своем округе.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Разрешаем безопасные методы (GET)
        
        # Получаем ID координат из URL
        coordinate_id = view.kwargs.get('pk')
        if coordinate_id is not None:
            try:
                coordinate = PlantationCoordinates.objects.get(id=coordinate_id)
                plantation = coordinate.plantation
                # Проверяем, принадлежит ли плантация округу пользователя
                return request.user.has_permission_for_plantation(plantation)
            except PlantationCoordinates.DoesNotExist:
                return False
        return False
