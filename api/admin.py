from django.contrib import admin
from .models import CustomUser, Plantation, PlantationCoordinates, Region, District, Fruits

# Inline admin for PlantationCoordinates
class PlantationCoordinatesInline(admin.StackedInline):
    model = PlantationCoordinates
    extra = 1  # Количество пустых полей для добавления координат

class PlantationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'district', 'status', 'established_date')
    search_fields = ('name', 'district__name')
    list_filter = ('district', 'status')
    inlines = [PlantationCoordinatesInline]  # Добавьте инлайн для координат

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "district":
            if request.user.is_superuser:
                # Если это суперпользователь, показываем все округа
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            else:
                # Фильтруем округа, которые доступны текущему пользователю
                kwargs["queryset"] = District.objects.filter(users=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Суперпользователь видит все
        # Ограничиваем видимость плантаций по округам
        return qs.filter(district__users=request.user)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')
    filter_horizontal = ('districts',)

class PlantationCoordinatesAdmin(admin.ModelAdmin):
    list_display = ('plantation', 'latitude', 'longitude')
    search_fields = ('plantation__id',)

class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    search_fields = ('name', 'region__name')
    list_filter = ('region',)

class FruitsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Регистрация моделей в админке
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Plantation, PlantationAdmin)
admin.site.register(PlantationCoordinates, PlantationCoordinatesAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Fruits, FruitsAdmin)
