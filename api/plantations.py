from rest_framework import serializers
from core.settings import BASE_URL
from .models import *
from .serializers import *

class PlantationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantationImage
        fields = ['image']  # Только поле image

    class Meta:
        model = PlantationFruitArea
        fields = ['fruit', 'area']


class PlantationListSerializer(serializers.ModelSerializer):
    district = serializers.CharField(source='district.name') 
    plantation_type = serializers.CharField(source='get_plantation_type_display')

    class Meta:
        model = Plantation
        fields = ['id', 'name', 'inn', 'district', 'plantation_type', 'status', 'established_date', 'is_checked', 'is_deleting']

class MapPlantationSerializer(serializers.ModelSerializer):
    district = serializers.CharField(source='district.name')
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = Plantation
        fields = ['id', 'name', 'district', 'coordinates']

    def get_coordinates(self, obj):
        coordinates = obj.coordinates.all()
        return [{"latitude": coord.latitude, "longitude": coord.longitude} for coord in coordinates]



class PlantationDetailSerializer(serializers.ModelSerializer):
    district = serializers.SerializerMethodField()  
    coordinates = serializers.SerializerMethodField()  
    fruit_areas = serializers.SerializerMethodField()  
    plantation_type = serializers.CharField(source='get_plantation_type_display')  
    images = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    is_deleting = serializers.BooleanField()  # Добавляем поле is_deleting

    class Meta:
        model = Plantation
        fields = ['id', 'name', 'inn', 'district', 'plantation_type', 'status', 
                  'established_date', 'total_area', 'is_checked', 'updated_at', 
                  'coordinates', 'images', 'fruit_areas', 'is_deleting', 'prev_data']

    def get_district(self, obj):
        return {
            'name': obj.district.name,
            'region': obj.district.region.name
        }

    def get_coordinates(self, obj):
        return [{'latitude': coord.latitude, 'longitude': coord.longitude} for coord in obj.coordinates.all()]

    def get_fruit_areas(self, obj):
        return [{'fruit': fruit.fruit.name, 'area': fruit.area} for fruit in obj.fruit_area.all()]

    def get_images(self, obj):
        return [f"{BASE_URL}{image.image.url}" for image in obj.images.all()]

    def get_updated_at(self, obj):
        tz = timezone.get_fixed_timezone(5 * 60)
        updated_at_tz = obj.updated_at.astimezone(tz)
        return {
            "date": updated_at_tz.strftime('%Y-%m-%d'),
            "time": updated_at_tz.strftime('%H:%M')
        }




class PlantationCoordinatesSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class PlantationFruitAreaSerializer(serializers.ModelSerializer):
    fruit = serializers.PrimaryKeyRelatedField(queryset=Fruits.objects.all())  # Для связи с фруктами
    area = serializers.FloatField()  # Площадь фрукта

    class Meta:
        model = PlantationFruitArea
        fields = ['fruit', 'area']


class PlantationCreateSerializer(serializers.ModelSerializer):
    coordinates = PlantationCoordinatesSerializer(many=True)
    fruit_area = PlantationFruitAreaSerializer(many=True)
    images = serializers.ListField(child=serializers.CharField())  # Изменено для работы с URL изображений

    class Meta:
        model = Plantation
        fields = ['name', 'inn', 'district', 'plantation_type', 'status', 'established_date', 'total_area', 'coordinates', 'fruit_area', 'images']

    def create(self, validated_data):
        # Извлекаем данные из validated_data
        coordinates_data = validated_data.pop('coordinates')
        fruit_area_data = validated_data.pop('fruit_area')
        images_data = validated_data.pop('images')

        # Создание самой плантации
        plantation = Plantation.objects.create(**validated_data)

        # Сохранение координат
        for coord in coordinates_data:
            PlantationCoordinates.objects.create(plantation=plantation, **coord)

        # Сохранение фруктовых площадей
        for fruit in fruit_area_data:
            PlantationFruitArea.objects.create(plantation=plantation, **fruit)

        # Сохранение изображений
        for image_url in images_data:
            PlantationImage.objects.create(plantation=plantation, image=image_url)

        return plantation



