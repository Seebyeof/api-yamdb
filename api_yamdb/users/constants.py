from django.core.validators import RegexValidator

from django.core.exceptions import ValidationError


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


def validate_username_not_me(value):
    """Запрещает использование зарезервированного имени 'me'."""

    if value.lower() == 'me':
        raise ValidationError(
            'Имя пользователя "me" зарезервировано системой.'
        )
