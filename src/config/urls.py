from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("products/", include(("apps.products.urls", "products"), namespace="products")),
    path('api/orders/', include('apps.orders.urls.ajax_urls')),
    path('orders/', include('apps.orders.urls.urls')),
    path("clients/", include(("apps.clients.urls", "clients"), namespace="clients")),
    path("", include(("apps.dashboard.urls", "dashboard"), namespace="dashboard")),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
