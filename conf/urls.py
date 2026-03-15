"""
URL configuration for shopping_list project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("", include("apps.core.urls")),
    path(
        "stavba", RedirectView.as_view(pattern_name="priority_list", permanent=False)
    ),
    path("admin/", admin.site.urls),
    path("shopping/", include("apps.shopping.urls")),
    path("recipe/", include("apps.recipe.urls")),
    path("clockify/", include("apps.clockify.urls")),
    path("house-construction/", include("apps.house_construction.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
