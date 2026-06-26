from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает доступ только администраторам для изменений.
    Остальные пользователи могут только читать (GET, HEAD, OPTIONS).
    Использует is_admin модели User (включает is_staff и is_superuser).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOnly(BasePermission):
    """Полный доступ только для администраторов и суперпользователей."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrModeratorOrAdmin(BasePermission):
    """
    Разрешает редактирование/удаление только:
    - Автору объекта
    - Модератору
    - Администратору
    Используется для отзывов и комментариев.
    """
    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        return (
            obj.author == user
            or getattr(user, 'is_moderator', False)
            or user.is_admin
        )
