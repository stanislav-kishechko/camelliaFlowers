import pytest
from django import forms

from apps.clients.enums import ClientStatusEnum
from apps.clients.forms import ClientForm
from apps.clients.models import Client


@pytest.mark.django_db
class TestClientForm:
    """Test suite for the ClientForm."""

    def test_form_has_correct_fields(self):
        """Test that form includes all required fields."""
        form = ClientForm()
        expected_fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "city",
            "notes",
            "client_type",
        ]
        assert list(form.fields.keys()) == expected_fields

    def test_form_field_types(self):
        """Test that form fields have correct types."""
        form = ClientForm()
        assert isinstance(form.fields["first_name"].widget, forms.TextInput)
        assert isinstance(form.fields["last_name"].widget, forms.TextInput)
        assert isinstance(form.fields["phone"].widget, forms.TextInput)
        assert isinstance(form.fields["email"].widget, forms.EmailInput)
        assert isinstance(form.fields["address"].widget, forms.TextInput)
        assert isinstance(form.fields["city"].widget, forms.TextInput)
        assert isinstance(form.fields["notes"].widget, forms.Textarea)
        assert isinstance(form.fields["client_type"].widget, forms.Select)

    def test_client_type_choices(self):
        """Test that client_type field has correct choices."""
        form = ClientForm()
        assert form.fields["client_type"].choices == ClientStatusEnum.choices

    def test_client_type_is_not_required(self):
        """Test that client_type field is optional."""
        form = ClientForm()
        assert form.fields["client_type"].required is False

    def test_client_type_initial_value(self):
        """Test that client_type has correct initial value."""
        form = ClientForm()
        assert form.fields["client_type"].initial == "regular"

    def test_form_valid_with_required_fields_only(self):
        """Test form is valid with only required fields."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "phone": "+380501234567",
        }
        form = ClientForm(data=data)
        assert form.is_valid()

    def test_form_invalid_without_first_name(self):
        """Test form is invalid without first name."""
        data = {
            "last_name": "Петренко",
            "phone": "+380501234567",
        }
        form = ClientForm(data=data)
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_form_invalid_without_last_name(self):
        """Test form is invalid without last name."""
        data = {
            "first_name": "Іван",
            "phone": "+380501234567",
        }
        form = ClientForm(data=data)
        assert not form.is_valid()
        assert "last_name" in form.errors

    def test_form_invalid_without_phone(self):
        """Test form is invalid without phone."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
        }
        form = ClientForm(data=data)
        assert not form.is_valid()
        assert "phone" in form.errors

    def test_form_valid_without_email(self):
        """Test form is valid without email (optional field)."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "phone": "+380501234567",
            "email": "",
        }
        form = ClientForm(data=data)
        assert form.is_valid()

    def test_form_valid_without_address(self):
        """Test form is valid without address (optional field)."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "phone": "+380501234567",
        }
        form = ClientForm(data=data)
        assert form.is_valid()

    def test_form_valid_without_city(self):
        """Test form is valid without city (optional field)."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "phone": "+380501234567",
        }
        form = ClientForm(data=data)
        assert form.is_valid()

    def test_form_valid_without_notes(self):
        """Test form is valid without notes (optional field)."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "phone": "+380501234567",
        }
        form = ClientForm(data=data)
        assert form.is_valid()

    def test_email_field_validation(self):
        """Test that email field validates email format."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "phone": "+380501234567",
            "email": "invalid-email",
        }
        form = ClientForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_valid_email_formats(self):
        """Test various valid email formats."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "123@example.com",
        ]

        for email in valid_emails:
            data = {
                "first_name": "Тест",
                "last_name": "Користувач",
                "phone": "+380501234567",
                "email": email,
            }
            form = ClientForm(data=data)
            assert form.is_valid(), f"Email {email} should be valid"

    def test_form_save_creates_client(self):
        """Test that saving form creates a Client instance."""
        data = {
            "first_name": "Іван",
            "last_name": "Петренко",
            "phone": "+380501234567",
            "email": "ivan@example.com",
        }
        form = ClientForm(data=data)
        assert form.is_valid()

        client = form.save()
        assert isinstance(client, Client)
        assert client.first_name == "Іван"
        assert client.last_name == "Петренко"
        assert client.phone == "+380501234567"
        assert client.email == "ivan@example.com"

    def test_form_save_updates_existing_client(self):
        """Test that form can update existing client."""
        client = Client.objects.create(
            first_name="Іван",
            last_name="Петренко",
            phone="+380501234567"
        )

        data = {
            "first_name": "Іван",
            "last_name": "Шевченко",
            "phone": "+380501234567",
            "email": "ivan@example.com",
        }
        form = ClientForm(data=data, instance=client)
        assert form.is_valid()

        updated_client = form.save()
        assert updated_client.id == client.id
        assert updated_client.last_name == "Шевченко"
        assert updated_client.email == "ivan@example.com"

    def test_first_name_widget_attributes(self):
        """Test first_name field widget has correct CSS classes."""
        form = ClientForm()
        widget_attrs = form.fields["first_name"].widget.attrs
        assert "class" in widget_attrs
        assert "focus:ring-pink-500" in widget_attrs["class"]

    def test_notes_textarea_rows(self):
        """Test notes field textarea has correct number of rows."""
        form = ClientForm()
        widget_attrs = form.fields["notes"].widget.attrs
        assert widget_attrs.get("rows") == 3

    def test_phone_placeholder(self):
        """Test phone field has placeholder."""
        form = ClientForm()
        widget_attrs = form.fields["phone"].widget.attrs
        assert "placeholder" in widget_attrs
        assert "+380" in widget_attrs["placeholder"]

    def test_form_meta_model(self):
        """Test form Meta specifies correct model."""
        assert ClientForm.Meta.model == Client

    def test_form_meta_fields(self):
        """Test form Meta includes correct fields."""
        expected_fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "city",
            "notes",
        ]
        assert ClientForm.Meta.fields == expected_fields

    def test_form_with_long_text_fields(self):
        """Test form handles long text in text fields."""
        data = {
            "first_name": "І" * 100,
            "last_name": "П" * 100,
            "phone": "+380501234567",
            "notes": "Н" * 1000,
        }
        form = ClientForm(data=data)
        assert form.is_valid()

    def test_form_with_special_characters(self):
        """Test form handles special characters."""
        data = {
            "first_name": "Іван-Петро",
            "last_name": "О'Брайен",
            "phone": "+380(50)123-45-67",
            "email": "user+tag@example.com",
        }
        form = ClientForm(data=data)
        assert form.is_valid()

    def test_form_instance_has_initial_data(self):
        """Test form populated with instance data."""
        client = Client.objects.create(
            first_name="Іван",
            last_name="Петренко",
            phone="+380501234567",
            email="ivan@example.com"
        )

        form = ClientForm(instance=client)
        assert form.initial["first_name"] == "Іван"
        assert form.initial["last_name"] == "Петренко"
        assert form.initial["phone"] == "+380501234567"
        assert form.initial["email"] == "ivan@example.com"
