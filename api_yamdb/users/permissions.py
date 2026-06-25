from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает доступ только администраторам для изменений.
    Остальные пользователи могут только читать (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        return (
            user.is_authenticated
            and (
                user.is_superuser
                or user.is_staff
                or getattr(user, 'role', None) == 'admin'
            )
        )


class IsAdminUser(BasePermission):
    """Полный доступ только для администраторов и суперпользователей."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin


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
            or user.is_moderator
            or user.is_admin
        )
