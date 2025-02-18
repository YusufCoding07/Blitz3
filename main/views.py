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
from .forms import UserProfileForm, DriverApplicationForm

# Home Page (Find Ride)
def home(request):
    return render(request, 'main/home.html')

# Profile Page
@login_required
def profile(request):
    # Get or create the user profile
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    driver_form = DriverApplicationForm(instance=profile)
    
    context = {
        'profile': profile,
        'driver_form': driver_form,
    }
    return render(request, 'main/profile.html', context)

# Map Page
def map_view(request):
    return render(request, 'main/map.html')

# Transactions Page
def transactions(request):
    user_transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'main/transactions.html', {'transactions': user_transactions})


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
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
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'main/update_profile.html', {'form': form})

@login_required
def driver_application(request):
    if request.method == 'POST':
        form = DriverApplicationForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_driver = True
            profile.save()
            messages.success(request, 'Your driver application has been approved!')
            return redirect('profile')
    return redirect('profile')