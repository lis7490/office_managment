from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только администраторам редактировать объекты.
    Обычные пользователи могут только просматривать.
    """
    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS запросы для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешаем редактирование только администраторам
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешаем редактирование только администраторам
        return request.user and request.user.is_staff