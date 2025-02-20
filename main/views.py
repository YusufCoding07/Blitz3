from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaction, UserProfile
from .forms import UserProfileForm, DriverApplicationForm, UserRegistrationForm
import logging
import traceback

logger = logging.getLogger('django')

# Home Page (Find Ride)
def home(request):
    try:
        context = {}
        if request.user.is_authenticated:
            logger.info(f"Authenticated user: {request.user.username}")
            try:
                # Change from UserProfile.objects.get() to a more defensive approach
                profile, created = UserProfile.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'phone_number': '',
                        'is_driver': False,
                        'has_valid_license': False,
                        'car_model': ''
                    }
                )
                logger.info(f"Profile {'created' if created else 'found'} for user: {profile}")
                context['profile'] = profile
            except Exception as e:
                logger.error(f"Error with profile: {str(e)}\n{traceback.format_exc()}")
                context['profile_error'] = str(e)
            
            try:
                transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
                logger.info(f"Found {len(transactions)} transactions")
                context['transactions'] = transactions
            except Exception as e:
                logger.error(f"Error getting transactions: {str(e)}\n{traceback.format_exc()}")
                context['transaction_error'] = str(e)
                
        return render(request, 'main/home.html', context)
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}\n{traceback.format_exc()}")
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

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
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

@login_required
def request_ride(request):
    if request.method == 'POST':
        # Add your ride request logic here
        return redirect('find_ride')
    return render(request, 'main/find_ride.html')

@login_required
def accept_ride(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Add your ride acceptance logic here
        messages.success(request, 'Ride accepted successfully!')
        return redirect('home')
    except Transaction.DoesNotExist:
        messages.error(request, 'Ride not found.')
        return redirect('home')

@login_required
def complete_ride(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Add your ride completion logic here
        messages.success(request, 'Ride completed successfully!')
        return redirect('home')
    except Transaction.DoesNotExist:
        messages.error(request, 'Ride not found.')
        return redirect('home')

@login_required
def cancel_ride(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Add your ride cancellation logic here
        messages.success(request, 'Ride cancelled successfully!')
        return redirect('home')
    except Transaction.DoesNotExist:
        messages.error(request, 'Ride not found.')
        return redirect('home')