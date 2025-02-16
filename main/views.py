from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Transaction  # Import your models if needed
from .models import Profile  # Add this line
from .forms import CustomUserCreationForm  # Add this line
from .forms import ProfileUpdateForm  # Add this line

# Home Page (Find Ride)
def home(request):
    return render(request, 'main/home.html')

# Profile Page
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
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
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data['email']
            user.save()
            
            # Create profile
            profile = Profile.objects.get_or_create(user=user)[0]
            profile.profile_picture = form.cleaned_data['profile_picture']
            profile.phone_number = form.cleaned_data['phone_number']
            profile.save()
            
            login(request, user)
            return redirect('home')
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

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.userprofile)
    
    return render(request, 'main/update_profile.html', {'form': form})