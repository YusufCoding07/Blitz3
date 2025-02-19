# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('transactions/', views.transactions, name='transactions'),  # Add this line
    path('map/', views.map_view, name='map'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('find-ride/', views.find_ride, name='find_ride'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('driver-application/', views.driver_application, name='driver_application'),
]