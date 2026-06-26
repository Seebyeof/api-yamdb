from rest_framework import mixins, viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.response import Response

from django.db.models import Avg
from django.shortcuts import get_object_or_404

from reviews.models import (
    Title,
    Category,
    Genre,
    Review,
)
from users.permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleCreateSerializer,
    ReviewCreateSerializer,
    CommentCreateSerializer
)
from reviews.filters import TitleFilter


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleCreateSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = TitleFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAdminOrReadOnly()]


class BaseNameSlugViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(BaseNameSlugViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseNameSlugViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Полноценный CRUD для отзывов через ModelViewSet."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_pk')
        )
        return title.reviews.all()

    def get_serializer_class(self):
        return ReviewCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [IsAuthorOrModeratorOrAdmin()]

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_pk')
        )

        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_pk'),
            title_id=self.kwargs.get('title_pk')
        )

        return review.comments.all()

    def get_serializer_class(self):
        return CommentCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [IsAuthorOrModeratorOrAdmin()]

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_pk'),
            title_id=self.kwargs.get('title_pk')
        )

        serializer.save(
            author=self.request.user,
            review=review
        )

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and 'pk' in kwargs:
            if not request.user.is_authenticated:
                response = Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                response = Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            self.headers = self.default_response_headers
            return self.finalize_response(request, response, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
