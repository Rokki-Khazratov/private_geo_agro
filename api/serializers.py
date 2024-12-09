from core.settings import BASE_URL
import pytz
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .models import *
from .plantations import *

import logging





class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'region']  # Включаем поле 'region' в сериализатор, чтобы его можно было установить
        read_only_fields = ['region']  # Сделаем поле region доступным только для чтения

    def create(self, validated_data):
        # Извлекаем или создаем регион, по умолчанию его можно присвоить пустым (например, если у вас уже есть Region в БД)
        region = Region.objects.first()  # Или добавьте свой способ получения региона
        district = District.objects.create(region=region, **validated_data)
        return district

class StatisticsSerializer(serializers.Serializer):
    total_issiqxonas = serializers.FloatField()
    total_uzumzors = serializers.FloatField()
    total_bogs = serializers.FloatField()
    total_area = serializers.FloatField() 
    total_fruit_areas = serializers.FloatField() 

    class Meta:
        fields = ['total_issiqxonas', 'total_uzumzors', 'total_bogs', 'total_area', 'total_fruit_areas']




# Настройка логгера
logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        return token

    def validate(self, attrs):
        # Получаем имя пользователя и пароль
        username = attrs.get("username")
        password = attrs.get("password")

        # Логируем попытку аутентификации
        logger.debug(f"Attempting to authenticate user: {username}")

        # Проверяем, что оба поля (username, password) присутствуют
        if not username or not password:
            raise AuthenticationFailed("Both username and password are required")

        # Пробуем аутентифицировать пользователя
        user = authenticate(username=username, password=password)
        
        if user is None:
            logger.warning(f"Authentication failed for user: {username}")
            raise AuthenticationFailed("Invalid credentials")

        logger.debug(f"Authenticated user: {user.id}")

        # Проверяем, есть ли у пользователя дополнительные обязательные поля
        missing_fields = []
        if not user.phone_number:
            missing_fields.append("phone_number")
        if not user.district:
            missing_fields.append("district")

        # Если есть недостающие поля, возвращаем ошибку
        if missing_fields:
            raise AuthenticationFailed(f"Missing required fields: {', '.join(missing_fields)}")

        # Обновляем время последнего входа
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


class Districterializer(serializers.ModelSerializer):
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())  # Ожидаем только ID региона

    class Meta:
        model = District
        fields = ['id', 'name', 'region']  # region теперь принимает только ID


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login']




class CustomUserCreateSerializer(serializers.ModelSerializer):
    # Теперь это будет работать с одиночным районом, а не с множественными
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=False)  # Только один район

    class Meta:
        model = CustomUser  # Используем кастомную модель
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'district']
    
    def create(self, validated_data):
        district = validated_data.pop('district', None)  # Извлекаем район
        user = CustomUser.objects.create_user(**validated_data)  # Создаём пользователя
        
        if district:
            user.district = district  # Присваиваем район
            user.save()  # Сохраняем пользователя
        
        return user




from rest_framework import serializers
from django.utils import timezone
import pytz
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    district = serializers.SerializerMethodField()  # Для преобразования district
    region = serializers.SerializerMethodField()  # Для преобразования region
    last_login = serializers.SerializerMethodField()  # Для отображения времени последнего входа с учётом часового пояса
    phone_number = serializers.SerializerMethodField()  # Для отображения номера телефона

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'phone_number', 'region', 'district', 'last_login']

    def get_phone_number(self, obj):
        return obj.phone_number

    def get_district(self, obj):
        """
        Метод для получения названия округа пользователя
        """
        if obj.district:
            return obj.district.name
        return None  # Если нет округа, возвращаем None

    def get_region(self, obj):
        """
        Метод для получения названия региона
        """
        district = obj.district  # Получаем округ пользователя
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