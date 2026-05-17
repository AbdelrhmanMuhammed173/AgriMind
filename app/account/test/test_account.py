from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from account.models import User


SIGNUP_URL = reverse('account:signup')
SIGNIN_URL = reverse('account:signin')
SIGNOUT_URL = reverse('account:signout')


class PublicAccountTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_signup_success(self):

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123"
        }

        res = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=payload['email']).exists())

    def test_user_signup_email_exists(self):

        User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123"
        }

        res = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):

        User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        payload = {
            "email": "test@example.com",
            "password": "testpass123"
        }

        res = self.client.post(SIGNIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data['tokens'])

    def test_user_login_fail(self):

        payload = {
            "email": "wrong@example.com",
            "password": "wrongpass"
        }

        res = self.client.post(SIGNIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthorized(self):

        res = self.client.post(SIGNOUT_URL, {"refresh": "fake-token"})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAccountTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        res = self.client.post(SIGNIN_URL, {
            "email": "test@example.com",
            "password": "testpass123"
        })

        self.token = res.data['tokens']['access']
        self.refresh = res.data['tokens']['refresh']

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )

    def test_logout_success(self):

        res = self.client.post(SIGNOUT_URL, {
            "refresh": self.refresh
        })

        self.assertEqual(res.status_code, status.HTTP_205_RESET_CONTENT)
