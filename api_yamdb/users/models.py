import re
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator
from django.db import models

USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
ROLE_MAX_LENGTH = 10
CONFIRMATION_CODE_MAX_LENGTH = 100

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message=(
        'Введите допустимое имя пользователя. '
        'Только буквы, цифры и символы @/./+/-/_.'
    )
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
        validators=[username_validator]
    )

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        validators=[EmailValidator()]
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
