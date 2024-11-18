from rest_framework import permissions
from api.models import *






class IsDistrictOwner(permissions.BasePermission):
    """
    Разрешение для проверки, имеет ли пользователь доступ к округу текущей плантации.
    """

    def has_permission(self, request, view):
        # Если пользователь аутентифицирован
        if not request.user.is_authenticated:
            return False
        
        # Суперпользователи могут создавать плантации в любом округе
        if request.user.is_superuser:
            return True

        # Проверяем, что пользователь связан с округом текущей плантации
        district_ids = request.user.districts.values_list('id', flat=True)
        return request.data.get('district') in district_ids








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
