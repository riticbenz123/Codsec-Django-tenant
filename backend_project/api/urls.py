from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('', views.api_root),
    path('register/', views.register),
    path('login/', views.login),
    path('my-permissions/', views.user_permissions),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]