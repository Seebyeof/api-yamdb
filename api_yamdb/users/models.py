from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя для проекта YaMDb."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    bio = models.TextField('Биография', blank=True)

    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
    )

    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором или админом."""
        return self.role == self.MODERATOR or self.is_admin
