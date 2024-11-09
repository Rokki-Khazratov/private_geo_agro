from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

    


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавляем дополнительную информацию в токен (например, user_id)
        token['user_id'] = user.id
        return token



class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']

class DistrictSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = District
        fields = ['id', 'name', 'region']

class FruitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fruits
        fields = ['id', 'name']


class PlantationCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantationCoordinates
        fields = ['id', 'plantation', 'latitude', 'longitude']

class PlantationSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    fruit_type = FruitsSerializer(many=True)
    coordinates = PlantationCoordinatesSerializer(many=True)
    plantation_type = serializers.CharField(source='get_plantation_type_display')  # Получаем текстовое значение из choice

    class Meta:
        model = Plantation
        fields = ['id', 'name', 'inn', 'district', 'plantation_type',
                'fruit_type', 'status', 'established_date', 'is_checked','coordinates']
