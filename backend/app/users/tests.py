from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com',
                                        username='tester',
                                        password='12345678')

    def test_user_should_sign_up(self):
        # given
        data = {
            'email': 'test2@example.com',
            'username': 'tester2',
            'password': '12345678',
            'password2': '12345678'
        }

        # when
        response = self.client.post('/api/auth/sign_up', data=data)

        # then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)