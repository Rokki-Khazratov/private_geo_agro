from rest_framework import generics
from .models import Plantation, PlantationCoordinates
from .serializers import PlantationSerializer, PlantationCoordinatesSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsDistrictOwner  # Нам нужно будет создать это разрешение

# Получить список всех плантаций или создать новую
class PlantationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # При создании плантации устанавливаем пользователя
        serializer.save(user=self.request.user)

# Получить, обновить или удалить плантацию по id
class PlantationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationSerializer
    permission_classes = [IsAuthenticated, IsDistrictOwner]

# Получить список координат плантаций или создать новые
class PlantationCoordinatesListCreateAPIView(generics.ListCreateAPIView):
    queryset = PlantationCoordinates.objects.all()
    serializer_class = PlantationCoordinatesSerializer
    permission_classes = [IsAuthenticated]

# Получить, обновить или удалить координаты плантации по id
class PlantationCoordinatesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlantationCoordinates.objects.all()
    serializer_class = PlantationCoordinatesSerializer
    permission_classes = [IsAuthenticated]
