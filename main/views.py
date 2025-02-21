from django.shortcuts import render, redirect
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
    form = RideSearchForm(request.GET)
    rides = Ride.objects.filter(status='open')
    
    if form.is_valid():
        pickup = form.cleaned_data.get('pickup')
        destination = form.cleaned_data.get('destination')
        date = form.cleaned_data.get('date')
        
        if pickup:
            rides = rides.filter(pickup_location__icontains=pickup)
        if destination:
            rides = rides.filter(dropoff_location__icontains=destination)
        if date:
            rides = rides.filter(date=date)
    
    context = {
        'form': form,
        'rides': rides,
        'show_results': request.GET.get('pickup') or request.GET.get('destination') or request.GET.get('date')
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

def terms(request):
    return render(request, 'main/terms.html')

@login_required
def create_ride(request):
    if not request.user.userprofile.is_driver:
        messages.error(request, "Only verified drivers can create rides.")
        return redirect('profile')

    if request.method == 'POST':
        form = RideCreateForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            ride.save()
            messages.success(request, "Ride created successfully!")
            return redirect('find_ride')
    else:
        form = RideCreateForm()
    
    return render(request, 'main/create_ride.html', {'form': form})