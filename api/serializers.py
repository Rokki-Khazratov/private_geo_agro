from rest_framework import serializers
from .models import Plantation, PlantationCoordinates, District, Region, Fruits, CustomUser

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

class PlantationSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    fruit_type = FruitsSerializer(many=True)

    class Meta:
        model = Plantation
        fields = ['id', 'name', 'inn', 'district', 'plantation_type', 'fruit_type', 'status', 'established_date', 'is_checked']

class PlantationCoordinatesSerializer(serializers.ModelSerializer):
    plantation = PlantationSerializer()

    class Meta:
        model = PlantationCoordinates
        fields = ['id', 'plantation', 'latitude', 'longitude']

class CustomUserSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'districts']
