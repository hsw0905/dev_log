from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}, }
        read_only_fields = ('id',)


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


class PasswordSerializer(ModelSerializer):
    new_password = serializers.CharField(max_length=128, min_length=8)
    new_password2 = serializers.CharField(max_length=128, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'password', 'new_password', 'new_password2']
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
            'new_password': {'write_only': True},
            'new_password2': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password2'):
            raise serializers.ValidationError('new_password, new_password2 must match')
        return attrs

    def validate_password(self, value):
        user = User.objects.get(id=self.context.get('request').user.id)
        if user.check_password(value):
            return value
        else:
            raise serializers.ValidationError('incorrect password')

    def update(self, instance, validated_data):
        instance.password = validated_data['new_password']
        instance.set_password(instance.password)
        instance.save()
        return instance
