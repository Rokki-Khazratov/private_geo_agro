from rest_framework import generics
from rest_framework import filters
from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.db.models import Q,Sum

from .permissions import IsDistrictOwner, IsDistrictOwnerForCoordinates
from .filters import PlantationFilter, StatisticsFilter
from .models import *
from .serializers import *
from .plantations import *



class UserInfoAPIView(APIView):

    def post(self, request, *args, **kwargs):
        token = request.data.get('access_token', None)

        if not token:
            raise AuthenticationFailed("Access token is missing in the request body")

        try:
            jwt_authentication = JWTAuthentication()
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
            user, _ = jwt_authentication.authenticate(request)
            user_data = UserInfoSerializer(user).data
            return Response(user_data)

        except AuthenticationFailed:
            raise AuthenticationFailed("Invalid token or token has expired")






@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        serializer = CustomUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Сохраняем пользователя
            return Response({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'districts': [district.name for district in user.districts.all()],
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=400)

        try:
            # Validate and get the refresh token
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                'access': access_token,
                'refresh': refresh_token,
            })
        except Exception as e:
            return Response({"detail": f"Error: {str(e)}"}, status=400)




@api_view(['POST'])
def create_district(request):
    if request.method == 'POST':
        # Проверяем, что region передан в запросе
        region_id = request.data.get('region', None)
        if not region_id:
            return Response({"error": "Region is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            region = Region.objects.get(id=region_id)  # Получаем регион по ID
        except Region.DoesNotExist:
            return Response({"error": "Region not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем новый округ с выбранным регионом
        request.data['region'] = region.id  # Устанавливаем ID региона в данные
        serializer = DistrictSerializer(data=request.data)

        if serializer.is_valid():
            district = serializer.save()  # Сохраняем новый округ
            return Response(DistrictSerializer(district).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_districts(request):
    if request.method == 'GET':
        districts = District.objects.all()
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_regions(request):
    if request.method == 'GET':
        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)






class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Только аутентифицированные пользователи могут видеть список
    # def get_queryset(self):
    #     """
    #     Ограничиваем доступ к пользователям в зависимости от прав (например, для суперпользователей).
    #     """
    #     queryset = super().get_queryset()
    #     if self.request.user.is_superuser:
    #         return queryset
    #     return queryset.filter(id=self.request.user.id)  # Только текущий пользователь видит себя

class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    # def get_object(self):
    #     """
    #     Возвращаем пользователя по ID, если это суперпользователь или сам текущий пользователь.
    #     """
    #     obj = super().get_object()
    #     if not self.request.user.is_superuser and obj != self.request.user:
    #         raise PermissionDenied("You do not have permission to view this user.")
    #     return obj







class StatisticsAPIView(generics.GenericAPIView):
    serializer_class = StatisticsSerializer
    def get(self, request, *args, **kwargs):
        plantations = Plantation.objects.all()
        total_issiqxonas = plantations.filter(plantation_type=2).aggregate(total_area=Sum('total_area'))['total_area'] or 0
        total_uzumzors = plantations.filter(plantation_type=1).aggregate(total_area=Sum('total_area'))['total_area'] or 0
        total_bogs = plantations.filter(plantation_type=3).aggregate(total_area=Sum('total_area'))['total_area'] or 0
        total_area = plantations.aggregate(total_area=Sum('total_area'))['total_area'] or 0
        total_fruit_areas = PlantationFruitArea.objects.aggregate(total_area=Sum('area'))['total_area'] or 0


        stats = {
            'total_issiqxonas': total_issiqxonas,
            'total_uzumzors': total_uzumzors,
            'total_bogs': total_bogs,
            'total_area': total_area,
            'total_fruit_areas': total_fruit_areas,
        }
        return Response(stats)





class PlantationCoordinatesListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PlantationCoordinatesSerializer
    permission_classes = [IsDistrictOwnerForCoordinates]
    def get_queryset(self):
        user_districts = self.request.user.districts.all()
        return PlantationCoordinates.objects.filter(plantation__district__in=user_districts)
    def perform_create(self, serializer):
        plantation = self.request.data.get('plantation')
        serializer.save(plantation=plantation)



class PlantationPagination(PageNumberPagination):
    page_size = 10  # количество объектов на страницу
    page_size_query_param = 'page_size'
    max_page_size = 100

class MapPlantationPagination(PageNumberPagination):
    page_size = 100 
    page_size_query_param = 'page_size'
    max_page_size = 1000





class PlantationListCreateAPIView(generics.ListAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationListSerializer
    pagination_class = PlantationPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = PlantationFilter 

class MapPlantationListAPIView(generics.ListAPIView):
    serializer_class = MapPlantationSerializer
    pagination_class = MapPlantationPagination

    def get_queryset(self):
        queryset = Plantation.objects.all()
        status = self.request.query_params.get('status', None)
        region_name = self.request.query_params.get('region', None)
        district_id = self.request.query_params.get('district', None)
        name = self.request.query_params.get('name', None)
        inn = self.request.query_params.get('inn', None)
        plantation_type = self.request.query_params.get('plantation_type', None)

        #filters   
        if status:
            queryset = queryset.filter(status=status)
        if region_name:
            queryset = queryset.filter(district__region__name__icontains=region_name)
        if district_id:
            queryset = queryset.filter(district__id=district_id)
        if plantation_type:
            queryset = queryset.filter(plantation_type=plantation_type)

        #search           
        if name:
            queryset = queryset.filter(name__icontains=name)
        if inn:
            queryset = queryset.filter(inn=inn)

        return queryset




class PlantationFullListAPIView(generics.ListAPIView):
    serializer_class = PlantationDetailSerializer
    pagination_class = PlantationPagination
    filter_backends = (filters.OrderingFilter,)  # Убираем DjangoFilterBackend, фильтрация будет вручную

    def get_queryset(self):
        queryset = Plantation.objects.all()

        # Получаем параметры фильтрации из запроса
        name = self.request.query_params.get('name', None)
        inn = self.request.query_params.get('inn', None)
        region_name = self.request.query_params.get('region_name', None)
        district_id = self.request.query_params.get('district_id', None)
        plantation_type = self.request.query_params.get('plantation_type', None)
        fruit_id = self.request.query_params.get('fruit_id', None)
        fruit_name = self.request.query_params.get('fruit_name', None)
        min_area = self.request.query_params.get('min_area', None)
        max_area = self.request.query_params.get('max_area', None)
        is_deleting = self.request.query_params.get('is_deleting', None)
        is_checked = self.request.query_params.get('is_checked', None)

        # Фильтруем по имени
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Фильтруем по INN
        if inn:
            queryset = queryset.filter(inn=inn)

        # Фильтруем по имени региона
        if region_name:
            queryset = queryset.filter(district__region__name__icontains=region_name)

        # Фильтруем по ID района
        if district_id:
            queryset = queryset.filter(district__id=district_id)

        # Фильтруем по типу плантации
        if plantation_type:
            queryset = queryset.filter(plantation_type=plantation_type)

        # Фильтруем по фруктам
        if fruit_id:
            queryset = queryset.filter(fruit_area__fruit__id=fruit_id)

        # Фильтруем по названию фрукта
        if fruit_name:
            queryset = queryset.filter(fruit_area__fruit__name__icontains=fruit_name)

        # Фильтруем по минимальной площади
        if min_area:
            queryset = queryset.filter(fruit_area__area__gte=min_area)

        # Фильтруем по максимальной площади
        if max_area:
            queryset = queryset.filter(fruit_area__area__lte=max_area)

        # Фильтруем по is_deleting
        if is_deleting:
            queryset = queryset.filter(is_deleting=is_deleting.lower() == 'true')

        # Фильтруем по is_checked
        if is_checked:
            queryset = queryset.filter(is_checked=is_checked.lower() == 'true')

        return queryset

    def perform_create(self, serializer):
        serializer.save()




class PlantationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationDetailSerializer

    def update(self, request, *args, **kwargs):
        plantation = self.get_object()

        # Получаем данные для обновления
        data = request.data

        # Проверяем, что поле is_deleting передано и обновляем его
        if 'is_deleting' in data:
            plantation.is_deleting = data['is_deleting']
        
        # Если есть другие данные для обновления, передаем их в сериализатор
        serializer = self.get_serializer(plantation, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Возвращаем успешный ответ с обновленными данными
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()


class PlantationCreateAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Received request data:", request.data)  # Отладка: что пришло в запросе

        # Пробуем сериализовать данные
        serializer = PlantationCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            print("Validated data:", serializer.validated_data)  # Отладка: проверка валидированных данных
            plantation = serializer.save()
            return Response(PlantationDetailSerializer(plantation).data, status=status.HTTP_201_CREATED)
        
        # Если невалидно, выводим ошибки
        print("Errors:", serializer.errors)  # Отладка: вывод ошибок
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

