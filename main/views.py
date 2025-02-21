from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaction, UserProfile, Ride
from .forms import UserProfileForm, DriverApplicationForm, UserRegistrationForm, RideCreateForm, RideSearchForm
import logging
import traceback
from django.utils import timezone
from django.db.models import Q

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
                transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
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
    # Get filter parameters from request
    pickup = request.GET.get('pickup', '')
    dropoff = request.GET.get('dropoff', '')
    sort = request.GET.get('sort', '-created_at')
    
    # Base queryset
    rides = Transaction.objects.filter(status='pending')
    
    # Apply filters if provided
    if pickup:
        rides = rides.filter(pickup_location__icontains=pickup)
    if dropoff:
        rides = rides.filter(dropoff_location__icontains=dropoff)
    
    # Apply sorting
    if sort == 'price_low':
        rides = rides.order_by('amount')
    elif sort == 'price_high':
        rides = rides.order_by('-amount')
    else:
        rides = rides.order_by('-created_at')
    
    context = {
        'rides': rides,
        'current_filters': {
            'pickup': pickup,
            'dropoff': dropoff,
            'sort': sort
        }
    }
    
    return render(request, 'main/find_ride.html', context)

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
    profile = request.user.userprofile
    
    if request.method == 'POST':
        form = DriverApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            profile.driver_document = form.cleaned_data['document']
            profile.driver_status = 'pending'
            profile.application_date = timezone.now()
            profile.save()
            messages.success(request, 'Application submitted for review!')
            return redirect('profile')
    else:
        form = DriverApplicationForm()

    return render(request, 'main/driver_application.html', {
        'form': form,
        'profile': profile
    })

@login_required
def request_ride(request):
    if request.method == 'POST':
        # Add your ride request logic here
        return redirect('find_ride')
    return render(request, 'main/find_ride.html')

@login_required
def accept_ride(request, ride_id):
    ride = get_object_or_404(Transaction, id=ride_id)
    if ride.status == 'pending':
        ride.driver = request.user
        ride.status = 'accepted'
        ride.save()
        messages.success(request, 'Ride accepted successfully!')
    else:
        messages.error(request, 'This ride is no longer available.')
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
            ride = form.save(commit=False)
            ride.user = request.user
            ride.save()
            messages.success(request, 'Ride request created successfully!')
            return redirect('transactions')
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