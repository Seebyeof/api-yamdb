from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    ReviewViewSet,
    CommentViewSet
)

router = DefaultRouter()
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')


urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/titles/<int:title_pk>/reviews/',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='title-reviews-list'
    ),
    path(
        'v1/titles/<int:title_pk>/reviews/<int:pk>/',
        ReviewViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='title-reviews-detail'
    ),
    path(
        'v1/titles/<int:title_pk>/reviews/<int:review_pk>/comments/',
        CommentViewSet.as_view(
            {'get': 'list', 'post': 'create'}
        ),
        name='review-comments-list'
    ),
    path(
        'v1/titles/<int:title_pk>/reviews/<int:review_pk>/comments/<int:pk>/',
        CommentViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='review-comments-detail'
    ),
]
