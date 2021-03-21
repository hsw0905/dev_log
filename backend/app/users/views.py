from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from users.models import User
from users.serializers import UserSignUpSerializer


class UserSignUpViewSet(mixins.CreateModelMixin,
                        GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
