import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .pagination import UserPagination

from .permissions import IsAdminOrReadOnly, IsAdminOnly
from .serializers import (
    SignUpSerializer,
    TokenObtainSerializer,
    UserMeSerializer,
    UserSerializer,
    UserAdminSerializer,
)

User = get_user_model()


def generate_confirmation_code():
    """Генерирует случайный код подтверждения из 6 цифр."""
    return str(random.randint(100000, 999999))


class SignUpView(generics.CreateAPIView):
    """Вью для регистрации и отправки кода подтверждения."""
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        username = data.get('username')

        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            if existing_user.username == username:
                existing_user.confirmation_code = generate_confirmation_code()
                existing_user.save()

                send_mail(
                    subject='Код подтверждения YaMDb',
                    message=(
                        f'Ваш код подтверждения: '
                        f'{existing_user.confirmation_code}'
                    ),
                    from_email=None,
                    recipient_list=[existing_user.email],
                    fail_silently=False,
                )

                return Response(
                    {'username': username, 'email': email},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'email': ['Пользователь с таким email уже существует.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            confirmation_code=generate_confirmation_code()
        )

        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {user.confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )


class TokenObtainView(generics.GenericAPIView):
    """Вью для получения JWT-токена по коду подтверждения."""
    serializer_class = TokenObtainSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.context['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'token': str(refresh.access_token)
        }, status=status.HTTP_200_OK)


class UserMeView(generics.RetrieveUpdateAPIView):
    """Вью для просмотра и обновления собственного профиля."""
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Возвращает текущего авторизованного пользователя."""
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями (только для админов)."""
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAdminOnly]
    lookup_field = 'username'
    pagination_class = UserPagination
    filter_backends = [SearchFilter]
    search_fields = ['username']

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия."""
        if self.action == 'list':
            return UserAdminSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT, разрешаем только PATCH."""
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
