# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('transactions/', views.transactions, name='transactions'),  # Add this line
    path('map/', views.map_view, name='map'),
    path('signup/', views.signup, name='signup'),
    path('signup/', views.signup, name='signup'),
]