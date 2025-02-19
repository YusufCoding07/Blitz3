from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaction, UserProfile
from .forms import CustomUserCreationForm  # Add this line
from .forms import UserProfileForm, DriverApplicationForm

# Home Page (Find Ride)
def home(request):
    try:
        if request.user.is_authenticated:
            context = {}
            try:
                profile = request.user.userprofile
                context['profile'] = profile
            except UserProfile.DoesNotExist:
                pass
            
            try:
                transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
                context['transactions'] = transactions
            except Transaction.DoesNotExist:
                pass
            
            return render(request, 'main/home.html', context)
        return render(request, 'main/home.html')
    except Exception as e:
        print(f"Error in home view: {str(e)}")
        return render(request, 'main/error.html', {'error': str(e)})

# Profile Page
@login_required
def profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Handle profile update
        profile.phone_number = request.POST.get('phone_number', '')
        profile.is_driver = request.POST.get('is_driver', False) == 'on'
        profile.has_valid_license = request.POST.get('has_valid_license', False) == 'on'
        profile.car_model = request.POST.get('car_model', '')
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Your profile has been updated!')
        return redirect('profile')
    
    return render(request, 'main/profile.html', {'profile': profile})

# Map Page
def map_view(request):
    return render(request, 'main/map.html')

# Transactions Page
@login_required
def transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'main/transactions.html', {'transactions': transactions})


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