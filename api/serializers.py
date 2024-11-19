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



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
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
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.all())  # Ожидаем только ID региона

    class Meta:
        model = District
        fields = ['id', 'name', 'region']  # region теперь принимает только ID


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login']




class CustomUserCreateSerializer(serializers.ModelSerializer):
    districts = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), many=True)
    
    class Meta:
        model = CustomUser  # Используем кастомную модель
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'districts']
    
    def create(self, validated_data):
        districts = validated_data.pop('districts', [])  # Извлекаем округа
        user = CustomUser.objects.create_user(**validated_data)  # Создаём пользователя
        
        user.districts.set(districts)  # Привязываем округа
        user.save()  # Сохраняем пользователя
        
        return user




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