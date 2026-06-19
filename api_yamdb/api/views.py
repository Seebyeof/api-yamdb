from rest_framework import viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticatedOrReadOnly
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import NotFound, PermissionDenied

from django.db.models import Avg

from reviews.models import (
    Title,
    Category,
    Genre,
    Review,
    Comment
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleCreateSerializer,
    ReviewSerializer,
    ReviewCreateSerializer,
    CommentSerializer,
    CommentCreateSerializer
)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleCreateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == ('list', 'retrieve'):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer

    def get_queryset(self):
        return Title.objects.annotate(rating=Avg('reviews__score'))


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class ReviewViewSet(viewsets.ModelViewSet):
    """Полноценный CRUD для отзывов через ModelViewSet."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_pk')
        if not Title.objects.filter(pk=title_id).exists():
            raise NotFound('Произведение не найдено.')
        return Review.objects.filter(title_id=title_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_pk')
        serializer.save(author=self.request.user, title_id=title_id)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не являетесь автором отзыва.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не являетесь автором отзыва.')
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Проверяем существование произведения и отзыва
        title_id = self.kwargs.get('title_pk')
        review_id = self.kwargs.get('review_pk')
        if not Title.objects.filter(pk=title_id).exists():
            raise NotFound('Произведение не найдено.')
        if not Review.objects.filter(pk=review_id, title_id=title_id).exists():
            raise NotFound('Отзыв не найден.')
        return Comment.objects.filter(review_id=review_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не автор комментария.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не автор комментария.')
        instance.delete()
