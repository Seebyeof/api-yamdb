from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    """Пагинация для списка пользователей."""
    page_size = 10
