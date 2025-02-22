from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RideSearchForm
from .models import Ride

def home(request):
    rides = Ride.objects.all()[:5]  # Example query
    return render(request, 'home.html', {'rides': rides})

@login_required
def profile(request):
    return render(request, 'profile.html')

def find_ride(request):
    form = RideSearchForm()
    return render(request, 'find_ride.html', {'form': form})