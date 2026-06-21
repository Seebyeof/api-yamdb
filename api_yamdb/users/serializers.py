import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, attrs):
        """
        Проверяет наличие полей, валидность, длину и уникальность.
        """
        errors = {}
        username = attrs.get('username')
        email = attrs.get('email')

        if not username:
            errors['username'] = ['Это поле обязательно.']
        else:
            if len(username) > 150:
                errors.setdefault('username', []).append(
                    'Поле username не должно быть длиннее 150 символов.'
                )
            elif not re.match(r'^[\w.@+-]+\Z', username):
                errors.setdefault('username', []).append(
                    'Поле username может содержать только буквы, '
                    'цифры и символы . @ + - _'
                )
            elif username.lower() == 'me':
                errors.setdefault('username', []).append(
                    'Использовать имя "me" запрещено.'
                )
            elif User.objects.filter(username=username).exists():
                errors.setdefault('username', []).append(
                    'Пользователь с таким username уже существует.'
                )

        if not email:
            errors['email'] = ['Это поле обязательно.']
        else:
            if len(email) > 254:
                errors.setdefault('email', []).append(
                    'Поле email не должно быть длиннее 254 символов.'
                )
            # Vérification unicité de l'email
            elif User.objects.filter(email=email).exists():
                errors.setdefault('email', []).append(
                    'Пользователь с таким email уже существует.'
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена по коду подтверждения."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        """Проверяет существование пользователя и код подтверждения."""
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Пользователь не найден.')

        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                'Неверный код подтверждения.'
            )

        self.context['user'] = user
        return data


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и редактирования профиля (/me)."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class UserAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для списка пользователей администратором (без id)."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для управления пользователями администратором."""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        """Проверяет уникальность email при создании/изменении."""
        instance = getattr(self, 'instance', None)
        qs = User.objects.filter(email=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return value
