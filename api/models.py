from django.db import models
from django.contrib.auth.models import User

# UTILS 
class HealthStatus(models.TextChoices):
    YAHSHI = 'yahshi', 'Yahshi'
    ORTACHA = 'ortacha', 'Ortacha'
    YOMON = 'yomon', 'Yomon'

# MODELS
class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Fruits(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Plantation(models.Model):
    PLANTATION_TYPE = (
        (1, "Uzumzorlar"),
        (2, "Issiqxonalar"),
        (3, "Bog'lar"),
    )
    name = models.CharField(max_length=50)
    inn = models.IntegerField()
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    plantation_type = models.IntegerField(choices=PLANTATION_TYPE)
    fruit_type = models.ManyToManyField(Fruits)
    
    status = models.CharField(
        max_length=30, 
        choices=HealthStatus.choices,
        default=HealthStatus.YAHSHI 
    )
    established_date = models.DateField()
    is_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"Plantation {self.id}"

class PlantationCoordinates(models.Model):
    plantation = models.ForeignKey(Plantation, related_name='coordinates', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"Coordinates for Plantation {self.plantation.id}"

# Добавление модели User
class CustomUser(User):
    districts = models.ManyToManyField(District, related_name='users', blank=True)

    def has_permission_for_plantation(self, plantation):
        """Проверяет, имеет ли пользователь доступ к плантации."""
        return plantation.district in self.districts.all()

    def __str__(self):
        return self.username
