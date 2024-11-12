from django.db import models
from django.utils import timezone  
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
    
    status = models.CharField(
        max_length=30, 
        choices=HealthStatus.choices,
        default=HealthStatus.YAHSHI 
    )
    established_date = models.DateField()
    is_checked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    total_area = models.FloatField(default=0)  # Общее количество гектаров для сада

    def save(self, *args, **kwargs):
        if not self.id or not self.is_checked:
            # Сбрасываем is_checked на False при любом изменении данных плантации
            self.is_checked = False
        # Убедитесь, что сравниваете только обычные поля, а не реляционные
        if self.pk:
            original = Plantation.objects.get(pk=self.pk)
            for field in self._meta.get_fields():
                if field.concrete and field.name != 'is_checked':  # Только реальные поля
                    if getattr(original, field.name) != getattr(self, field.name):
                        self.is_checked = False
                        break
        super(Plantation, self).save(*args, **kwargs)


    def __str__(self):
        return f"Plantation {self.id}"

class PlantationFruitArea(models.Model):
    plantation = models.ForeignKey(Plantation, on_delete=models.CASCADE, related_name='fruit_area')
    fruit = models.ForeignKey(Fruits, on_delete=models.CASCADE)
    area = models.FloatField()  # Площадь, которую занимает данный фрукт в гектар

    def __str__(self):
        return f"{self.fruit.name} area in plantation {self.plantation.id} - {self.area} ha"

class PlantationImage(models.Model):
    plantation = models.ForeignKey(Plantation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='plantation_images/') 

    def __str__(self):
        return f"Image for Plantation {self.plantation.name}"


class PlantationCoordinates(models.Model):
    plantation = models.ForeignKey(Plantation, related_name='coordinates', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"Coordinates for Plantation {self.plantation.id}"

# Добавление модели User
class CustomUser(User):
    districts = models.ManyToManyField(District, related_name='users', blank=True)
    phone_number = models.CharField(max_length=255)

    def has_permission_for_plantation(self, plantation):
        """Проверяет, имеет ли пользователь доступ к плантации."""
        return plantation.district in self.districts.all()
        
    def has_access_to_district(self, district):
        """
        Проверяет, есть ли у пользователя доступ к конкретному округу.
        """
        return district in self.districts.all()

    def __str__(self):
        return self.username
    
