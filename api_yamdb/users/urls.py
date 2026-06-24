from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignUpView, TokenObtainView, UserMeView, UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('v1/users/me/', UserMeView.as_view(), name='user_me'),

    path('v1/', include(router.urls)),
]
