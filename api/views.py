from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework_simplejwt.views import TokenObtainPairView


from .permissions import IsDistrictOwner, IsDistrictOwnerForCoordinates
from .models import *
from .serializers import *



class PlantationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(district__in=self.request.user.districts.all())

    def perform_create(self, serializer):
        serializer.save()



# Получить, обновить или удалить плантацию по id
class PlantationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationSerializer
    # permission_classes = [IsAuthenticated, IsDistrictOwner]



class PlantationCoordinatesListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PlantationCoordinatesSerializer
    permission_classes = [IsDistrictOwnerForCoordinates]

    def get_queryset(self):
        # Получаем округа, к которым имеет доступ текущий пользователь
        user_districts = self.request.user.districts.all()
        # Фильтруем координаты по округам, к которым имеет доступ пользователь
        return PlantationCoordinates.objects.filter(plantation__district__in=user_districts)

    def perform_create(self, serializer):
        # При создании координат плантации, добавляем округ, к которому относится плантация
        plantation = self.request.data.get('plantation')
        serializer.save(plantation=plantation)




class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer