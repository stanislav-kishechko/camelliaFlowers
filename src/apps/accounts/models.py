from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Represents a user in the system with an email-based authentication mechanism.

    This class extends the default AbstractUser class to use an email field as the
    username field for authentication. The class also customizes the verbose
    names for display purposes and sets ordering by the date the user joined.

    :ivar email: Stores the unique email address of the user used for authentication.
    :type email: models.EmailField
    """
    email = models.EmailField(
        "email адреса",
        unique=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Represents a user profile related to a specific user account.

    The UserProfile model is used to store additional information about
    a user, such as their phone number, city, position, biography, and
    whether they are a top manager. This model is linked to the User
    model through a one-to-one relationship.

    :ivar user: The user associated with this profile.
    :ivar phone: The phone number of the user. Can be left blank.
    :ivar city: The city of residence of the user. Can be left blank.
    :ivar position: The position/job title of the user. Defaults to
        "Менеджер з продажу".
    :ivar bio: A biography for the user to describe themselves. Can
        be left blank.
    :ivar is_top_manager: Indicates if the user is a top manager.
        Defaults to False.
    :ivar created_at: The timestamp when this profile was created.
        Automatically set on creation.
    :ivar updated_at: The timestamp for when this profile was last
        updated. Automatically updated on save.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    phone = models.CharField(
        "Телефон",
        max_length=20,
        blank=True
    )
    city = models.CharField(
        "Місто",
        max_length=100,
        blank=True
    )
    position = models.CharField(
        "Посада",
        max_length=100,
        default="Менеджер з продажу"
    )
    bio = models.TextField(
        "Про себе",
        blank=True
    )
    is_top_manager = models.BooleanField(
        "Топ менеджер",
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"

    def __str__(self):
        return f"Профіль {self.user.email}"
