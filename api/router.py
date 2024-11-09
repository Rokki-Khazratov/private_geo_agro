from django.urls import path
from .views import PlantationListCreateAPIView, PlantationRetrieveUpdateDestroyAPIView, PlantationCoordinatesListCreateAPIView, PlantationCoordinatesRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('plantations/', PlantationListCreateAPIView.as_view(), name='plantation-list-create'),
    path('plantations/<int:pk>/', PlantationRetrieveUpdateDestroyAPIView.as_view(), name='plantation-retrieve-update-destroy'),
    path('plantation-coordinates/', PlantationCoordinatesListCreateAPIView.as_view(), name='plantation-coordinates-list-create'),
    path('plantation-coordinates/<int:pk>/', PlantationCoordinatesRetrieveUpdateDestroyAPIView.as_view(), name='plantation-coordinates-retrieve-update-destroy'),
]
