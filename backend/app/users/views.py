from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.models import User
from users.serializers import UserSignUpSerializer, UserSerializer, PasswordSerializer


class UserSignUpViewSet(mixins.CreateModelMixin,
                        GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer


class UserViewSet(mixins.CreateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'sign_up':
            return UserSignUpSerializer
        elif self.action == 'change_password':
            return PasswordSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        return Response(status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['POST'])
    def sign_up(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def sign_in(self, request):
        password = request.data.get('password')
        user = get_object_or_404(User, email=request.data.get('email'),
                                 username=request.data.get('username'))

        if user.check_password(password):
            tokens = user.tokens()
            return Response({'refresh_token': tokens.get('refresh'),
                             'access_token': tokens.get('access'),
                             'id': user.id,
                             'email': user.email,
                             'username': user.username,
                             },
                            status=status.HTTP_201_CREATED)
        data = {
            "message": "incorrect password"
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH'])
    def change_password(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
