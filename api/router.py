from django.urls import path
from .views import *

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain'),

    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'), 

    path('plantations/', PlantationListCreateAPIView.as_view(), name='plantation-list-create'),
    path('plantations/<int:pk>/', PlantationRetrieveUpdateDestroyAPIView.as_view(), name='plantation-retrieve-update-destroy'),

    path('statistics/', StatisticsAPIView.as_view(), name='statistics-for-admin'),
]
