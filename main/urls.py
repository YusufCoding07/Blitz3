
# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL now points to your home.html
]
path('profile/', views.profile, name='profile'),