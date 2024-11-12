from core.settings import BASE_URL
import pytz
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .models import *




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавляем дополнительную информацию в токен
        token['user_id'] = user.id
        return token

    def validate(self, attrs):
        # Аутентифицируем пользователя
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        
        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        # Обновляем last_login на текущий момент
        user.last_login = timezone.now()
        user.save()

        # Создаем и возвращаем токен
        refresh = self.get_token(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }



class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']

class DistrictSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = District
        fields = ['id', 'name', 'region']





class UserSerializer(serializers.ModelSerializer):
    districts = serializers.SerializerMethodField()  # Для преобразования districts
    region = serializers.SerializerMethodField()  # Для преобразования region
    last_login = serializers.SerializerMethodField()  # Для отображения времени последнего входа с учётом часового пояса
    phone_number = serializers.SerializerMethodField()  # Для отображения времени последнего входа с учётом часового пояса

    class Meta:
        model = get_user_model()
        fields = ['id', 'username','first_name','last_name','phone_number', 'region', 'districts', 'last_login']

    def get_phone_number(self,obj):
        return obj.phone_number

    def get_districts(self, obj):
        """
        Метод для получения только названия округов пользователя
        """
        return [district.name for district in obj.districts.all()]

    def get_region(self, obj):
        """
        Метод для получения только названия региона
        """
        district = obj.districts.first()  # Получаем первый округ пользователя
        if district:
            return district.region.name  # Возвращаем название региона
        return None  # Если нет округа, возвращаем None

    def get_last_login(self, obj):
        """
        Метод для получения последнего времени входа с учётом часового пояса.
        """
        if obj.last_login:
            # Устанавливаем правильный часовой пояс для Ташкента (+5)
            tz = pytz.timezone('Asia/Tashkent')
            # Преобразуем время в нужный часовой пояс
            last_login_time = obj.last_login.astimezone(tz)
            # Форматируем время в строку
            return last_login_time.strftime('%Y-%m-%d %H:%M:%S')
        return None



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




class PlantationFruitAreaSerializer(serializers.ModelSerializer):
    fruit = FruitsSerializer()  # Сериализуем фрукт
    area = serializers.FloatField()  # Площадь фрукта

    class Meta:
        model = PlantationFruitArea
        fields = ['fruit', 'area']

class PlantationSerializer(serializers.ModelSerializer):
    district = serializers.SerializerMethodField()  
    coordinates = serializers.SerializerMethodField()  
    fruit_areas = serializers.SerializerMethodField()  
    plantation_type = serializers.CharField(source='get_plantation_type_display')  
    images = serializers.SerializerMethodField()  
    updated_at = serializers.SerializerMethodField()  

    class Meta:
        model = Plantation
        fields = ['id', 'name', 'inn', 'district', 'plantation_type', 'status', 
                  'established_date', 'is_checked', 'updated_at', 'coordinates', 
                  'images', 'fruit_areas']

    def get_district(self, obj):
        return {
            'name': obj.district.name,
            'region': obj.district.region.name
        }

    def get_coordinates(self, obj):
        return [{'latitude': coord.latitude, 'longitude': coord.longitude} for coord in obj.coordinates.all()]

    def get_fruit_areas(self, obj):
        # Получаем площади фруктов через связь PlantationFruitArea
        return [{'fruit': fruit.fruit.name, 'area': fruit.area} for fruit in obj.fruit_area.all()]

    def get_images(self, obj):
        return [f"{BASE_URL}{image.image.url}" for image in obj.images.all()]

    def get_updated_at(self, obj):
        tz = timezone.get_fixed_timezone(5 * 60)  # Время для Ташкента: UTC+5
        updated_at_tz = obj.updated_at.astimezone(tz)
        return {
            "date": updated_at_tz.strftime('%Y-%m-%d'),
            "time": updated_at_tz.strftime('%H:%M')
        }
