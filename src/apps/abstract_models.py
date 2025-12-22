from django.db import models


class AbstractDatetimeModel(models.Model):
    """
    Abstract base class for models with datetime fields.

    This class provides `created_at` and `updated_at` fields for tracking the
    creation and last update timestamps of a model instance. It is intended to
    be used as an abstract base class that can be inherited by other models.

    :ivar created_at: Timestamp indicating when the model instance was created.
    :type created_at: datetime.datetime
    :ivar updated_at: Timestamp indicating when the model instance was last
        updated.
    :type updated_at: datetime.datetime
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Створено",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Оновлено",
    )

    class Meta:
        abstract = True
