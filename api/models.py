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
    total_area = models.FloatField(default=0)  # Общее количество гектаров для сада

    is_checked = models.BooleanField(default=False)
    is_deleting = models.BooleanField(default=False)  # Добавляем поле для отслеживания плантации на удаление
    updated_at = models.DateTimeField(auto_now=True)
    prev_data = models.JSONField(null=True, blank=True)  # Для хранения предыдущих данных плантации

    def save(self, *args, **kwargs):
        # Проверяем, если is_checked = True и есть изменения, вызываем clear()
        if self.is_checked and self.prev_data:
            self.clear()

        if not self.id or not self.is_checked:
            # Сбрасываем is_checked на False при любом изменении данных плантации
            self.is_checked = False

        # Если это не новый объект, проверяем изменения
        if self.pk:
            original = Plantation.objects.get(pk=self.pk)
            
            # Проверка, были ли изменения в важных полях
            changes = {}
            for field in self._meta.get_fields():
                if field.concrete and field.name != 'is_checked' and field.name != 'prev_data':
                    # Сравниваем старое значение с новым
                    if getattr(original, field.name) != getattr(self, field.name):
                        changes[field.name] = {
                            'old': getattr(original, field.name),
                            'new': getattr(self, field.name)
                        }

            # Если изменения есть, сохраняем старые данные
            if changes:
                self.prev_data = changes
            else:
                self.prev_data = None  # Если изменений нет, очищаем поле prev_data

        super(Plantation, self).save(*args, **kwargs)

    def clear(self):
        """
        Метод очистки данных: сбрасываем prev_data и выполняем другие действия при необходимости.
        """
        print(f"Clearing previous data for Plantation {self.id}...")
        self.prev_data = None  # Очищаем предшествующие данные
        # Можно добавить дополнительные действия для очистки, если необходимо.

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
    

