from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from django.db.models import Q



from .permissions import IsDistrictOwner, IsDistrictOwnerForCoordinates
from .filters import PlantationFilter
from .models import *
from .serializers import *


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Только аутентифицированные пользователи могут видеть список
    # def get_queryset(self):
    #     """
    #     Ограничиваем доступ к пользователям в зависимости от прав (например, для суперпользователей).
    #     """
    #     queryset = super().get_queryset()
    #     if self.request.user.is_superuser:
    #         return queryset
    #     return queryset.filter(id=self.request.user.id)  # Только текущий пользователь видит себя

class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    # def get_object(self):
    #     """
    #     Возвращаем пользователя по ID, если это суперпользователь или сам текущий пользователь.
    #     """
    #     obj = super().get_object()
    #     if not self.request.user.is_superuser and obj != self.request.user:
    #         raise PermissionDenied("You do not have permission to view this user.")
    #     return obj






class PlantationCoordinatesListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PlantationCoordinatesSerializer
    permission_classes = [IsDistrictOwnerForCoordinates]
    def get_queryset(self):
        user_districts = self.request.user.districts.all()
        return PlantationCoordinates.objects.filter(plantation__district__in=user_districts)
    def perform_create(self, serializer):
        plantation = self.request.data.get('plantation')
        serializer.save(plantation=plantation)



class PlantationPagination(PageNumberPagination):
    page_size = 10  # количество объектов на страницу
    page_size_query_param = 'page_size'
    max_page_size = 100





class PlantationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationListSerializer
    pagination_class = PlantationPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = PlantationFilter 

    def perform_create(self, serializer):
        serializer.save()

class PlantationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationDetailSerializer



