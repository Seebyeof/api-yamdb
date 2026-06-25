from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает доступ только администраторам для изменений.
    Остальные пользователи могут только читать (GET, HEAD, OPTIONS).
    Полный доступ также для суперпользователей и staff.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
<<<<<<< HEAD
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return (
            obj.author == user
            or user.is_moderator
            or user.is_admin
=======

        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser
                or request.user.is_staff
            )
        )


class IsAdminOnly(BasePermission):
    """Полный доступ только для администраторов и суперпользователей."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser
                or request.user.is_staff
            )
>>>>>>> 5ad6c4d (fix: валидация полей User, константы, объединение пермишенов и регистрация в админке)
        )
