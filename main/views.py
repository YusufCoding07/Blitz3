from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaction, UserProfile, Ride
from .forms import UserProfileForm, DriverApplicationForm, UserRegistrationForm, RideCreateForm, RideSearchForm, SignUpForm
import logging
import traceback
from django.utils import timezone
from django.db.models import Q
from django import forms
from django.db import transaction
from decimal import Decimal

logger = logging.getLogger('django')

# Home Page (Find Ride)
def home(request):
    nearby_rides = []
    
    if request.user.is_authenticated:
        user_location = request.user.userprofile.location
        # Get rides that match user's location or nearby areas
        nearby_rides = Transaction.objects.filter(
            Q(status='pending') &
            (Q(pickup_location__icontains=user_location) |
             Q(dropoff_location__icontains=user_location))
        ).order_by('-created_at')[:5]  # Show 5 most recent nearby rides
    
    context = {
        'nearby_rides': nearby_rides
    }
    return render(request, 'main/home.html', context)

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
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
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

@login_required
def find_ride(request):
    # Initialize form
    form = RideSearchForm()
    rides = Transaction.objects.filter(status='pending')
    
    # Process form data if submitted
    if request.GET:
        form = RideSearchForm(request.GET)
        if form.is_valid():
            pickup = form.cleaned_data.get('pickup')
            dropoff = form.cleaned_data.get('dropoff')
            
            if pickup:
                rides = rides.filter(pickup_location__icontains=pickup)
            if dropoff:
                rides = rides.filter(dropoff_location__icontains=dropoff)
    
    # Handle sorting
    sort = request.GET.get('sort', '-created_at')
    if sort == 'price_low':
        rides = rides.order_by('amount')
    elif sort == 'price_high':
        rides = rides.order_by('-amount')
    else:
        rides = rides.order_by('-created_at')

    return render(request, 'main/find_ride.html', {
        'form': form,
        'rides': rides,
        'current_filters': {
            'pickup': request.GET.get('pickup', ''),
            'dropoff': request.GET.get('dropoff', ''),
            'sort': sort
        }
    })

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

class DriverApplicationForm(forms.Form):
    car_model = forms.CharField(max_length=100)
    license_file = forms.FileField(label='Driver License')  # Changed from 'document' to 'license_file'

@login_required
def driver_application(request):
    if request.method == 'POST':
        form = DriverApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.userprofile
            profile.car_model = form.cleaned_data['car_model']
            profile.license_file = form.cleaned_data['license_file']
            profile.driver_status = 'pending'
            profile.is_driver = True  # Set this flag when they apply
            profile.application_date = timezone.now()
            profile.save()
            
            messages.success(request, 'Your driver application has been submitted successfully!')
            return redirect('profile')
    else:
        form = DriverApplicationForm()
    
    return render(request, 'main/driver_application.html', {'form': form})

@login_required
def request_ride(request):
    if request.method == 'POST':
        # Add your ride request logic here
        return redirect('find_ride')
    return render(request, 'main/find_ride.html')

@login_required
def accept_ride(request, ride_id):
    try:
        # First try to get the ride
        ride = get_object_or_404(Transaction, id=ride_id)
        
        # Check if ride is still pending
        if ride.status != 'pending':
            messages.error(request, 'This ride is no longer available.')
            return redirect('find_ride')
        
        # Don't allow accepting your own ride
        if request.user == ride.user:
            messages.error(request, 'You cannot accept your own ride.')
            return redirect('find_ride')
        
        try:
            with transaction.atomic():
                # Update the ride status
                ride.status = 'accepted'
                ride.driver = request.user  # Add this line to track who accepted the ride
                ride.save()
                
                # Create payment transaction for the passenger
                passenger_transaction = Transaction.objects.create(
                    user=ride.user,  # passenger
                    amount=Decimal(str(-ride.amount)),  # Convert to Decimal explicitly
                    status='completed',
                    transaction_type='payment',  # Add transaction type
                    pickup_location=ride.pickup_location,
                    dropoff_location=ride.dropoff_location,
                    description=f'Payment for ride from {ride.pickup_location} to {ride.dropoff_location}'
                )
                
                # Create earning transaction for the accepting user
                driver_transaction = Transaction.objects.create(
                    user=request.user,  # accepting user
                    amount=Decimal(str(ride.amount)),  # Convert to Decimal explicitly
                    status='completed',
                    transaction_type='earning',  # Add transaction type
                    pickup_location=ride.pickup_location,
                    dropoff_location=ride.dropoff_location,
                    description=f'Earnings from ride {ride.pickup_location} to {ride.dropoff_location}'
                )
                
                logger.info(f'Ride {ride_id} accepted successfully. Payment: {passenger_transaction.id}, Earning: {driver_transaction.id}')
                messages.success(request, 'Ride accepted successfully!')
                return redirect('transactions')
                
        except Exception as e:
            logger.error(f'Error in transaction processing for ride {ride_id}: {str(e)}')
            messages.error(request, f'Transaction error: {str(e)}')
            return redirect('find_ride')
            
    except Exception as e:
        logger.error(f'Error accepting ride {ride_id}: {str(e)}')
        messages.error(request, f'Error accepting ride: {str(e)}')
        return redirect('find_ride')

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

def terms(request):
    return render(request, 'main/terms.html')

@login_required
def create_ride(request):
    if request.method == 'POST':
        form = RideCreateForm(request.POST)
        if form.is_valid():
            try:
                ride = form.save(commit=False)
                ride.user = request.user
                ride.status = 'pending'
                ride.transaction_type = 'ride'  # Set the transaction type
                ride.driver = None  # Initialize driver as None
                ride.save()
                messages.success(request, 'Ride posted successfully!')
                return redirect('find_ride')
            except Exception as e:
                messages.error(request, f'Error creating ride: {str(e)}')
                return redirect('create_ride')
    else:
        form = RideCreateForm()
    
    return render(request, 'main/create_ride.html', {'form': form})

@login_required
def search_rides(request):
    if request.method == 'POST':
        form = RideSearchForm(request.POST)
        if form.is_valid():
            pickup = form.cleaned_data['pickup_location']
            dropoff = form.cleaned_data['dropoff_location']
            rides = Transaction.objects.filter(
                status='pending',
                pickup_location__icontains=pickup,
                dropoff_location__icontains=dropoff
            ).order_by('-created_at')
            return render(request, 'main/search_results.html', {'rides': rides})
    else:
        form = RideSearchForm()
    return render(request, 'main/search_rides.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile with location
            UserProfile.objects.create(
                user=user,
                location=form.cleaned_data.get('location')
            )
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})