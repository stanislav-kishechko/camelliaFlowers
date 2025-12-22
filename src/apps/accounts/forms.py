from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class LoginForm(forms.Form):
    """
    Form for user login.

    This form is used to authenticate users by collecting their username (or email),
    password, and an optional "remember me" preference. It includes custom styling
    for the input fields and ensures proper validation.

    :ivar username: Email address or username for user authentication.
    :type username: forms.CharField
    :ivar password: Password associated with the username or email.
    :type password: forms.CharField
    :ivar remember_me: Indicates whether the user wants to stay logged in.
    :type remember_me: forms.BooleanField
    """
    username = forms.CharField(
        label="Email або ім\"я користувача",
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500",
            "placeholder": "manager@camellia.com"
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500",
            "placeholder": "••••••••"
        })
    )
    remember_me = forms.BooleanField(
        label="Запам\"ятати мене",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "w-4 h-4 text-pink-500 border-gray-300 rounded "
                     "focus:ring-pink-500"
        })
    )


class RegisterForm(forms.ModelForm):
    """
    A form for user registration.

    This form allows users to register by providing their first name, last name,
    email, username, and password. It validates that the email and username are
    unique and ensures the provided passwords match and adhere to password
    validation rules.

    :ivar password: Password field with a custom widget for entering secure input.
    :ivar password_confirm: Password confirmation field to ensure the user enters the
        same password correctly.
    """
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500",
            "placeholder": "••••••••"
        })
    )
    password_confirm = forms.CharField(
        label="Підтвердження паролю",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500",
            "placeholder": "••••••••"
        })
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500",
                "placeholder": "Марія"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500",
                "placeholder": "Коваленко"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500",
                "placeholder": "maria@camellia.com"
            }),
            "username": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500",
                "placeholder": "maria_kovalenko"
            }),
        }

    def clean_email(self):
        """
        Validates and processes the email field from the cleaned form data. The method
        checks if the provided email already exists in the database and raises a
        ValidationError if so. Otherwise, it returns the validated email.

        :raises ValidationError: If a user with the given email already exists.
        :rtype: str
        :return: The validated email address.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Користувач з таким email вже існує")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Користувач з таким username вже існує")
        return username

    def clean(self):
        """
        Cleans and validates the form data by ensuring the password and
        password confirmation match, and verifying the password against
        validation rules.

        This method extends the base class `clean` method, performing
        additional validation specific to password handling.

        :return: Dictionary containing the cleaned form data, if validation is
            successful.
        :rtype: dict

        :raises ValidationError: If passwords do not match or fail to meet the
            validation criteria.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Паролі не співпадають")

            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error("password", e)

        return cleaned_data


class ProfileForm(forms.ModelForm):
    """
    A form for updating user profiles, including user fields and additional profile
    fields.

    This form extends ModelForm and links to the User model for updating basic user
    information such as first name, last name, and email. It also provides additional
    fields like phone, city, position, and bio for managing profile-specific data.
    These additional fields are initialized from the provided profile instance, if any.

    :ivar phone: Phone number of the user.
    :type phone: forms.CharField
    :ivar city: City of residence for the user.
    :type city: forms.CharField
    :ivar position: Position (job title or role) of the user.
    :type position: forms.CharField
    :ivar bio: Short biography or description about the user.
    :type bio: forms.CharField
    :ivar Meta.model: The User model that this form is based on.
    :type Meta.model: django.contrib.auth.models.User
    :ivar Meta.fields: Fields from the User model included in the form
        (first name, last name, email).
    :type Meta.fields: list
    :ivar Meta.widgets: Custom widgets for styling User model fields.
    :type Meta.widgets: dict
    """
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500"
        })
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500"
        })
    )
    position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500"
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500",
            "rows": 3
        })
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500"
            }),
        }

    def __init__(self, *args, profile_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile_instance = profile_instance

        if profile_instance:
            self.fields["phone"].initial = profile_instance.phone
            self.fields["city"].initial = profile_instance.city
            self.fields["position"].initial = profile_instance.position
            self.fields["bio"].initial = profile_instance.bio

    def save(self, commit=True):
        user = super().save(commit=commit)

        if self.profile_instance:
            self.profile_instance.phone = self.cleaned_data.get("phone", "")
            self.profile_instance.city = self.cleaned_data.get("city", "")
            self.profile_instance.position = self.cleaned_data.get("position", "")
            self.profile_instance.bio = self.cleaned_data.get("bio", "")
            if commit:
                self.profile_instance.save()

        return user


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Поточний пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500"
        })
    )
    new_password1 = forms.CharField(
        label="Новий пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500"
        })
    )
    new_password2 = forms.CharField(
        label="Підтвердіть новий пароль",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 "
                     "rounded-lg focus:ring-2 focus:ring-pink-500"
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise ValidationError("Невірний поточний пароль")
        return old_password

    def clean(self):
        """
        Cleans and validates the form data. This method ensures that the two password fields
        (new_password1 and new_password2) are consistent and meet password validation rules.
        If they do not match or fail validation, appropriate errors are raised or added
        to the form.

        :raises ValidationError: If the new_password1 and new_password2 fields do not match.
        :raises ValidationError: If the new_password1 does not meet defined password
            validation criteria.
        :return: A dictionary of cleaned form data after validation.
        :rtype: dict
        """
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("Нові паролі не співпадають")

            try:
                validate_password(new_password1, self.user)
            except ValidationError as e:
                self.add_error("new_password1", e)

        return cleaned_data

    def save(self, commit=True):
        """
        Sets a new password for the user instance and saves the user if specified.

        This method updates the password of the user object using the
        provided "new_password1" field from cleaned_data. If the `commit`
        flag is set to True, the user object is saved to persist the change.

        :param commit: Whether to save the user object after setting the new
            password. Defaults to True.
        :type commit: bool
        :return: The updated user object with the new password set.
        :rtype: User
        """
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user
