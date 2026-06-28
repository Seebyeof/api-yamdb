from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models

from .constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    CONFIRMATION_CODE_MAX_LENGTH,
    username_validator,
    validate_username_not_me,
)


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

    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[username_validator, validate_username_not_me],
    )

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        validators=[EmailValidator()],
    )

    bio = models.TextField('Биография', blank=True)

    role = models.CharField(
        'Роль',
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
    )

    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CONFIRMATION_CODE_MAX_LENGTH,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""

        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""

        return self.role == self.MODERATOR or self.is_admin
