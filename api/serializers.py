from core.settings import BASE_URL
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


class PlantationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantationImage
        fields = ['image']  # Только поле image

class PlantationCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantationCoordinates
        fields = ['id', 'plantation', 'latitude', 'longitude']



from django.utils import timezone
from rest_framework import serializers

class PlantationSerializer(serializers.ModelSerializer):
    district = serializers.SerializerMethodField()  # Для преобразования district
    fruit_type = FruitsSerializer(many=True)
    coordinates = serializers.SerializerMethodField()  # Для преобразования coordinates
    plantation_type = serializers.CharField(source='get_plantation_type_display')  # Получаем текстовое значение из choice
    images = serializers.SerializerMethodField()  # Для преобразования images
    updated_at = serializers.SerializerMethodField()  # Для преобразования updated_at в date и time

    class Meta:
        model = Plantation
        fields = ['id', 'name', 'inn', 'district', 'plantation_type',
                  'fruit_type', 'status', 'established_date', 'is_checked', 'updated_at', 'coordinates', 'images']

    # Метод для преобразования district
    def get_district(self, obj):
        return {
            'name': obj.district.name,
            'region': obj.district.region.name
        }

    # Метод для преобразования coordinates
    def get_coordinates(self, obj):
        return [{'latitude': coord.latitude, 'longitude': coord.longitude} for coord in obj.coordinates.all()]

    # Метод для преобразования images
    def get_images(self, obj):
        return [f"{BASE_URL}{image.image.url}" for image in obj.images.all()]

    # Метод для преобразования updated_at в date и time
    def get_updated_at(self, obj):
        # Учитываем часовой пояс Ташкента (+5)
        tz = timezone.get_fixed_timezone(5 * 60)  # Время для Ташкента: UTC+5
        updated_at_tz = obj.updated_at.astimezone(tz)

        # Возвращаем форматированные date и time
        return {
            "date": updated_at_tz.strftime('%Y-%m-%d'),  # Форматируем дату
            "time": updated_at_tz.strftime('%H:%M')     # Форматируем время
        }
