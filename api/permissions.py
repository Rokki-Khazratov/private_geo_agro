from rest_framework import permissions
from api.models import *






class IsDistrictOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        district = request.data.get('district')
        return request.user.district == district  # Провер








class IsDistrictOwnerForCoordinates(permissions.BasePermission):
    def has_permission(self, request, view):
        district = request.data.get('district')
        return request.user.district == district  # 