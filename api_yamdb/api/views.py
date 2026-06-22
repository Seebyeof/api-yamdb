from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    MethodNotAllowed
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)

from django.db.models import Avg

from reviews.models import (
    Title,
    Category,
    Genre,
    Review,
    Comment
)
from users.permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAdminOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer

    def get_queryset(self):
        queryset = Title.objects.annotate(rating=Avg('reviews__score'))
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre__slug=genre)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAdminOrReadOnly()]

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAdminOrReadOnly()]

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ReviewViewSet(viewsets.ModelViewSet):
    """Полноценный CRUD для отзывов через ModelViewSet."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

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
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [IsAuthorOrModeratorOrAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
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
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [IsAuthorOrModeratorOrAdmin()]

    def perform_create(self, serializer):
        serializer.save()

    def initial(self, request, *args, **kwargs):
        if request.method.lower() == 'post' and (
            'pk' in kwargs
            or 'comment_pk' in kwargs
        ):
            if not request.user or not request.user.is_authenticated:
                raise NotAuthenticated()
            raise MethodNotAllowed('POST')
        return super().initial(request, *args, **kwargs)
