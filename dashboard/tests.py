from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='usuario01', password='test-password-123'
        )

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
    def test_valid_credentials_allow_dashboard_access(self, mock_get):
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

    def test_logout_only_accepts_post_and_redirects_to_login(self):
        self.client.force_login(self.user)
        get_response = self.client.get(reverse('logout'))
        post_response = self.client.post(reverse('logout'))

        self.assertEqual(get_response.status_code, 405)
        self.assertRedirects(post_response, reverse('login'))
