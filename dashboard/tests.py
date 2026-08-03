from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='usuario01', password='test-password-123'
        )
        cls.user_without_permission = get_user_model().objects.create_user(
            username='usuario02', password='test-password-123'
        )
        cls.superuser = get_user_model().objects.create_superuser(
            username='admin', password='test-password-123'
        )
        cls.permission = Permission.objects.get(codename='index_viewer')
        cls.user.user_permissions.add(cls.permission)

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse('dashboard_index'))
        self.assertRedirects(response, '/login/?next=/')

    def test_invalid_credentials_show_error(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'usuario01', 'password': 'incorrect'},
        )
        self.assertContains(response, 'Invalid username or password.')

    @patch('dashboard.views.requests.get')
    def test_user_with_permission_can_access_dashboard(self, mock_get):
        api_response = Mock()
        api_response.json.return_value = []
        mock_get.return_value = api_response

        logged_in = self.client.login(
            username='usuario01', password='test-password-123'
        )
        response = self.client.get(reverse('dashboard_index'))

        self.assertTrue(logged_in)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'usuario01')

    def test_user_without_permission_receives_custom_403(self):
        self.client.force_login(self.user_without_permission)

        response = self.client.get(reverse('dashboard_index'))

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        self.assertContains(response, '403', status_code=403)

    @patch('dashboard.views.requests.get')
    def test_superuser_can_access_dashboard(self, mock_get):
        api_response = Mock()
        api_response.json.return_value = []
        mock_get.return_value = api_response
        self.client.force_login(self.superuser)

        response = self.client.get(reverse('dashboard_index'))

        self.assertEqual(response.status_code, 200)

    def test_logout_only_accepts_post_and_redirects_to_login(self):
        self.client.force_login(self.user)
        get_response = self.client.get(reverse('logout'))
        post_response = self.client.post(reverse('logout'))

        self.assertEqual(get_response.status_code, 405)
        self.assertRedirects(post_response, reverse('login'))
