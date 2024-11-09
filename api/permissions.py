from api.models import Plantation
from rest_framework import permissions

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
