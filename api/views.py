from rest_framework import generics
from rest_framework import filters
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





class PlantationListCreateAPIView(generics.ListAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationListSerializer
    pagination_class = PlantationPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = PlantationFilter 

class PlantationFullListAPIView(generics.ListAPIView):
    queryset = Plantation.objects.all()
    serializer_class = PlantationDetailSerializer
    pagination_class = PlantationPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = PlantationFilter 

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

