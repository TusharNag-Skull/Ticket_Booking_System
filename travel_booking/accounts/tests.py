from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsTests(TestCase):
    def test_register_and_login(self):
        resp = self.client.post(
            reverse("accounts:register"),
            {
                "username": "charlie",
                "email": "c@example.com",
                "phone": "123456",
                "password1": "StrongPass12345",
                "password2": "StrongPass12345",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username="charlie").exists())

        # Logout and login
        self.client.get(reverse("accounts:logout"))
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "charlie", "password": "StrongPass12345"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)

# Create your tests here.
