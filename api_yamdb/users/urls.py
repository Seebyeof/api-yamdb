from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignUpView, TokenObtainView, UserMeView, UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('users/me/', UserMeView.as_view(), name='user_me'),

    path('', include(router.urls)),
]
