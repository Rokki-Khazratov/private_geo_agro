from django.utils import timezone

class UpdateLastLoginMiddleware:
    """
    Middleware для обновления поля last_login для каждого аутентифицированного пользователя.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем аутентифицированного пользователя
        user = request.user
        
        if user.is_authenticated:
            # Обновляем поле last_login на текущее время
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])  # Обновляем только last_login, чтобы избежать излишних сохранений
        
        # Пропускаем запрос дальше
        response = self.get_response(request)
        return response
