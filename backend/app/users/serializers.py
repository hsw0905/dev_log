from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSignUpSerializer(ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'},
                                      write_only=True,
                                      max_length=128,
                                      min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}, }
        read_only_fields = ('id',)

    def validate_password(self, value):
        min_length = 8
        if len(value) < min_length:
            raise serializers.ValidationError('password is too short, at least 8 characters required')
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError('password, password2 must match')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return super().create(validated_data)
