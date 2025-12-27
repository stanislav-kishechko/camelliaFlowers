"""Admin configuration for the clients app.

Docstring style: Google. Language: English.
"""
from __future__ import annotations

from django.contrib import admin

from apps.clients.models import Client

admin.site.register(Client)
