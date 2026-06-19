from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

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

titles_router = NestedDefaultRouter(router, r'titles', lookup='title')
titles_router.register(r'reviews', ReviewViewSet, basename='title-reviews')

reviews_router = NestedDefaultRouter(
    titles_router,
    r'reviews',
    lookup='review'
)
reviews_router.register(
    r'comments',
    CommentViewSet,
    basename='review-comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(titles_router.urls)),
    path('v1/', include(reviews_router.urls)),
]
