from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaction  # Import your models if needed
from .models import UserProfile  # Updated this line
from .forms import CustomUserCreationForm  # Add this line
from .forms import ProfileUpdateForm  # Add this line

# Home Page (Find Ride)
def home(request):
    return render(request, 'main/home.html')

# Profile Page
@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'main/profile.html', {'profile': profile})

# Map Page
def map_view(request):
    return render(request, 'main/map.html')

# Transactions Page
def transactions(request):
    transactions = []  # Use an empty list for now
    return render(request, 'main/transactions.html', {'transactions': transactions})


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Profile creation should happen automatically via signals
            login(request, user)  # Automatically log in the user
            return redirect('profile')  # Redirect to profile page instead of login
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

# Login Page
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html')

# Logout Page
def logout_view(request):
    logout(request)
    return redirect('home')

def find_ride(request):
    return render(request, 'main/find_ride.html')

from django.core.exceptions import ObjectDoesNotExist

@login_required
def update_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'main/update_profile.html', {'form': form})