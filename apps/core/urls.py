from django.urls import path
from django.contrib.auth import views as auth_views

from .views import manifest_view, service_worker_view

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('manifest.json', manifest_view, name='manifest'),
    path('sw.js', service_worker_view, name='service_worker'),
]