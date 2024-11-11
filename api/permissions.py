from rest_framework import permissions
from api.models import *

class IsDistrictOwner(permissions.BasePermission):
    """
    Разрешение, которое проверяет, имеет ли пользователь доступ к плантации в конкретном округе.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Разрешаем безопасные методы (GET)
        
        # Получаем ID плантации из URL
        plantation_id = view.kwargs.get('pk')
        if plantation_id is not None:
            try:
                plantation = Plantation.objects.get(id=plantation_id)
                return request.user.has_permission_for_plantation(plantation)
            except Plantation.DoesNotExist:
                return False

        return False

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
