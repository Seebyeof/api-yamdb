from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from reviews.models import Title
from .serializers import TitleReadSerializer, TitleCreateSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleCreateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:  # create
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return TitleReadSerializer
        return TitleCreateSerializer
