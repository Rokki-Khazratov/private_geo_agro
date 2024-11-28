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
    fruit_areas = serializers.SerializerMethodField()  # Обновляем метод для получения фруктовых областей
    plantation_type = serializers.CharField(source='get_plantation_type_display')
    images = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    is_deleting = serializers.BooleanField()
    established_date = serializers.DateField(format='%Y-%m-%d')  # Форматируем дату в строку

    class Meta:
        model = Plantation
        fields = [
            'id', 'name', 'inn', 'district', 'plantation_type', 'status', 
            'established_date', 'total_area', 'is_checked', 
            'updated_at', 'coordinates', 'images', 'fruit_areas', 'is_deleting', 'prev_data'
        ]
    
    def get_district(self, obj):
        return {
            'name': obj.district.name,
            'region': obj.district.region.name
        }

    def get_coordinates(self, obj):
        return [{'latitude': coord.latitude, 'longitude': coord.longitude} for coord in obj.coordinates.all()]

    def get_fruit_areas(self, obj):
        return [
            {
                'fruit': fruit.fruit.name,
                'variety': fruit.variety.name if fruit.variety else None,  # Добавляем сорт фрукта
                'area': fruit.area
            } 
            for fruit in obj.fruit_area.all()
        ]

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
    variety = serializers.PrimaryKeyRelatedField(queryset=FruitVariety.objects.all())  # Ожидаем только ID
    fruit = serializers.SerializerMethodField()

    class Meta:
        model = PlantationFruitArea
        fields = ['fruit', 'variety', 'area']

    def get_fruit(self, obj):
        """Получаем фрукт через сорт."""
        return obj.variety.fruit.id if obj.variety else None





class FruitVarietySerializer(serializers.ModelSerializer):
    fruit_name = serializers.CharField(source='fruit.name')  # Отображаем имя фрукта, связанного с сортом
    class Meta:
        model = FruitVariety
        fields = ['id', 'name', 'fruit','fruit_name']


# class PlantationCreateSerializer(serializers.ModelSerializer):
#     coordinates = PlantationCoordinatesSerializer(many=True)
#     fruit_area = PlantationFruitAreaSerializer(many=True)
#     images = serializers.ListField(child=serializers.CharField())  # Работает с URL изображений

#     class Meta:
#         model = Plantation
#         fields = ['name', 'inn', 'district', 'plantation_type', 'status', 'established_date', 'total_area', 'coordinates', 'fruit_area', 'images']

#     def create(self, validated_data):
#         print(f"Validated data: {validated_data}")  # Лог для отслеживания валидированных данных

#         coordinates_data = validated_data.pop('coordinates')
#         fruit_area_data = validated_data.pop('fruit_area')
#         images_data = validated_data.pop('images')

#         # Получаем пользователя из контекста запроса
#         user = self.context['request'].user
#         print(f"User: {user}") 

#         if not user.districts.exists():
#             print("User is not assigned to any district")  # Лог, если у пользователя нет привязанных районов
#             raise serializers.ValidationError("User must be assigned to a district")

#         # Привязываем плантацию к району пользователя
#         validated_data['district'] = user.districts.first()  # Привязываем к первому району пользователя

#         # Создание самой плантации
#         plantation = Plantation.objects.create(**validated_data)

#         # Сохранение координат
#         for coord in coordinates_data:
#             PlantationCoordinates.objects.create(plantation=plantation, **coord)

#         # Сохранение фруктовых площадей
#         for fruit in fruit_area_data:
#             PlantationFruitArea.objects.create(plantation=plantation, **fruit)

#         # Сохранение изображений
#         for image_url in images_data:
#             PlantationImage.objects.create(plantation=plantation, image=image_url)

#         print(f"Created plantation: {plantation}")  # Лог для отслеживания созданной плантации

#         return plantation



class PlantationCreateSerializer(serializers.ModelSerializer):
    coordinates = PlantationCoordinatesSerializer(many=True)
    fruit_area = PlantationFruitAreaSerializer(many=True)
    images = serializers.ListField(child=serializers.CharField())  # Работает с URL изображений

    class Meta:
        model = Plantation
        fields = ['name', 'inn', 'district', 'plantation_type', 'status', 'established_date', 'total_area', 'coordinates', 'fruit_area', 'images']

    def create(self, validated_data):
        coordinates_data = validated_data.pop('coordinates')
        fruit_area_data = validated_data.pop('fruit_area')
        images_data = validated_data.pop('images')

        # Проверяем, что все необходимые данные для fruit_area и другие поля присутствуют
        for fruit in fruit_area_data:
            if 'fruit' not in fruit or 'variety' not in fruit or 'area' not in fruit:
                print(fruit)
                # print(fruit,request.data['variety'] )
                raise serializers.ValidationError("Each fruit area entry must include 'fruit', 'variety', and 'area'.")

        plantation = Plantation.objects.create(**validated_data)

        for coord in coordinates_data:
            PlantationCoordinates.objects.create(plantation=plantation, **coord)

        for fruit in fruit_area_data:
            PlantationFruitArea.objects.create(plantation=plantation, **fruit)

        for image_url in images_data:
            PlantationImage.objects.create(plantation=plantation, image=image_url)

        return plantation

