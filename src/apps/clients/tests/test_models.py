"""Тести моделі Client."""
import pytest


@pytest.mark.django_db
class TestClientModel:
    def test_full_name_and_initials(self, client_obj):
        assert client_obj.full_name == "Іван Іванов"
        assert client_obj.initials == "ІІ"

    def test_flags_toggle(self, client_obj):
        client_obj.make_vip()
        client_obj.refresh_from_db()
        assert client_obj.is_vip is True

        client_obj.remove_vip()
        client_obj.refresh_from_db()
        assert client_obj.is_vip is False

        client_obj.deactivate()
        client_obj.refresh_from_db()
        assert client_obj.is_active is False

        client_obj.activate()
        client_obj.refresh_from_db()
        assert client_obj.is_active is True
