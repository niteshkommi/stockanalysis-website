from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/',views.register, name='register'),
    path('accounts/login/',views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
]
