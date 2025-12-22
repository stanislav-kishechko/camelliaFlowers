import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages


@pytest.mark.django_db
class TestAccountsViews:
    def test_login_page_redirects_if_authenticated(self, client, user):
        client.login(username="manager", password="pass1234")
        resp = client.get(reverse("accounts:login"))
        assert resp.status_code == 200

    def test_login_success_with_email_and_sets_message(self, client, user):
        url = reverse("accounts:login")
        resp = client.post(url, {"username": "manager@example.com", "password": "pass1234"}, follow=True)
        assert resp.status_code == 200
        assert resp.request["PATH_INFO"].endswith(reverse("dashboard:dashboard"))

    def test_login_failure_shows_error(self, client):
        url = reverse("accounts:login")
        resp = client.post(url, {"username": "unknown@example.com", "password": "wrong"}, follow=True)
        assert resp.status_code == 200
        msgs = [m.message for m in get_messages(resp.wsgi_request)]
        assert any("Невірний" in m for m in msgs)

    def test_register_redirects_if_authenticated(self, client, user):
        client.login(username="manager", password="pass1234")
        resp = client.get(reverse("accounts:register"))
        assert resp.status_code == 200

    def test_register_success_creates_user_and_redirects_to_login(self, client):
        url = reverse("accounts:register")
        data = {
            "first_name": "Марія",
            "last_name": "Коваленко",
            "email": "newuser@example.com",
            "username": "maria_k",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        resp = client.post(url, data, follow=True)
        assert resp.status_code == 200
        User = get_user_model()
        assert User.objects.filter(email="newuser@example.com").exists()
        # After register we should be on login page
        assert resp.request["PATH_INFO"].endswith(reverse("accounts:login"))
        msgs = [m.message for m in get_messages(resp.wsgi_request)]
        assert any("Реєстрацію завершено" in m for m in msgs)

    def test_register_invalid_shows_error(self, client):
        url = reverse("accounts:register")
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "email": "bad@example.com",
            "username": "ivan_p",
            "password": "abc",
            "password_confirm": "xyz",  # mismatch
        }
        resp = client.post(url, data)
        assert resp.status_code == 200
        msgs = [m.message for m in get_messages(resp.wsgi_request)]
        assert any("виправте помилки" in m for m in msgs)

    def test_logout_redirects_to_login(self, client, user):
        client.login(username="manager", password="pass1234")
        resp = client.get(reverse("accounts:logout"))
        assert resp.status_code == 302
        assert reverse("accounts:login") in resp.url

    def test_profile_requires_login(self, client):
        resp = client.get(reverse("accounts:profile"))
        assert resp.status_code == 302
        assert reverse("accounts:login") in resp.url

    def test_profile_get_and_post_updates_profile(self, client, user):
        client.login(username="manager", password="pass1234")

        resp = client.get(reverse("accounts:profile"))
        assert resp.status_code == 302

        data = {
            "form_type": "personal",
            "first_name": "Тест",
            "last_name": "Юзер",
            "email": "manager@example.com",
            "phone": "+380501112233",
            "city": "Київ",
            "position": "Менеджер",
            "bio": "Про мене",
        }
        resp2 = client.post(reverse("accounts:profile"), data, follow=True)
        assert resp2.status_code == 200
