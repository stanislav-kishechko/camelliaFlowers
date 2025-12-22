from django.db import models


class ClientStatusEnum(models.TextChoices):
    """
    Enumeration for client status.

    This class represents the different statuses that a client can have. It is
    part of the Django TextChoices, allowing usage in model fields with
    pre-defined choices and human-readable labels. The statuses include options
    for active clients, VIP clients, and new clients.
    """
    ACTIVE = "Active", "Активний"
    VIP = "VIP", "VIP"
    NEW = "New", "Новий"
