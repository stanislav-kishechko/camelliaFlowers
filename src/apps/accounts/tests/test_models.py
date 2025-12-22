import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_and_str(self):
        User = get_user_model()
        u = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="pass1234",
            first_name="Test",
            last_name="User",
        )
        assert str(u) == "user@example.com"
        assert u.check_password("pass1234")

    def test_email_unique(self):
        User = get_user_model()
        User.objects.create_user(
            username="u1",
            email="unique@example.com",
            password="pass1234",
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                username="u2",
                email="unique@example.com",
                password="pass1234",
            )
