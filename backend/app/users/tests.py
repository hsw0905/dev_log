from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserTestCase(APITestCase):
    def setUp(self):
        self.test_email = 'test@example.com'
        self.test_username = 'tester'
        self.test_password = '12345678'
        self.test_new_password = '12345679'
        self.user = User.objects.create(email=f'{self.test_email}',
                                        username=f'{self.test_username}',
                                        password=f'{self.test_password}')

    def test_user_should_sign_up(self):
        """
        Request : POST - /api/users/sign_up
        """
        # given
        data = {
            'email': 'new@example.com',
            'username': 'tester2',
            'password': f'{self.test_password}',
            'password2': f'{self.test_password}'
        }

        # when
        response = self.client.post('/api/users/sign_up', data=data)

        # then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        user_response = Munch(response.data)
        self.assertTrue(user_response.id)
        self.assertEqual(user_response.email, data['email'])
        self.assertEqual(user_response.username, data['username'])

    def test_user_should_sign_in(self):
        """
        Request : POST - /api/users/sign_in
        """
        # given
        data = {
            'email': f'{self.test_email}',
            'username': f'{self.test_username}',
            'password': f'{self.test_password}',
        }

        # when
        response = self.client.post('/api/users/sign_in', data=data)

        # then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        user_response = Munch(response.data)
        self.assertTrue(user_response.refresh_token)
        self.assertTrue(user_response.access_token)
        self.assertTrue(user_response.id)
        self.assertEqual(user_response.email, data['email'])
        self.assertEqual(user_response.username, data['username'])

    def test_should_change_password(self):
        """
        Request : PATCH - /api/users/123/change_password
        """
        entry = User.objects.get(email=f'{self.test_email}')
        self.client.force_authenticate(user=entry)
        data = {'password': f'{self.test_password}',
                'new_password': f'{self.test_new_password}',
                'new_password2': f'{self.test_new_password}'}

        response = self.client.patch(f'/api/users/{entry.id}/change_password', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
