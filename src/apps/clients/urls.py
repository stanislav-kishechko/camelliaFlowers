"""URL configuration for the clients app.

Docstring style: Google. Language: English.
"""
from __future__ import annotations

from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.ClientListView.as_view(), name="clients"),
    path("create/", views.ClientCreateView.as_view(), name="client_create"),
    path("<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client_edit"),
    path("<int:pk>/delete/", views.ClientDeleteView.as_view(), name="client_delete"),
    path("<int:pk>/toggle-vip/", views.ClientToggleVIPView.as_view(), name="client_toggle_vip"),
]
