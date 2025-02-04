from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL
    path('profile/', views.profile, name='profile'),
    path('map/', views.map_view, name='map'),
]