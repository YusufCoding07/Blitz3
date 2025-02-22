from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm  # Use Django's built-in form temporarily
from .forms import RideSearchForm  # Import the form
from .models import Ride
from .forms import RideCreateForm
from .models import Transaction
from django.contrib.auth import logout


import logging
logger = logging.getLogger('django')
# Then copy all your view functions here 
# Home Page (Find Ride)
def home(request):
    context = {}
    
    if request.user.is_authenticated:
        # Get nearby rides from the Ride model, not Transaction
        nearby_rides = Ride.objects.filter(
            status='available'
        ).exclude(
            driver=request.user
        ).order_by('-date', '-time')[:5]
        
        # Get user's rides
        if hasattr(request.user, 'userprofile') and request.user.userprofile.is_driver:
            user_rides = Ride.objects.filter(
                driver=request.user
            ).order_by('-date')[:5]
        else:
            user_rides = Ride.objects.filter(
                passenger=request.user
            ).order_by('-date')[:5]
        
        context.update({
            'nearby_rides': nearby_rides,
            'user_rides': user_rides,
        })
    
    return render(request, 'main/home.html', context)
# Profile Page
@login_required
def profile(request):
    # Get all transactions for this user
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate statistics
    earnings = transactions.filter(amount__gt=0)
    spendings = transactions.filter(amount__lt=0)
    
    # Calculate totals (handle None cases)
    total_earnings = earnings.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spendings = spendings.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate averages (handle None cases)
    avg_earnings = earnings.aggregate(Avg('amount'))['amount__avg'] or 0
    avg_spendings = spendings.aggregate(Avg('amount'))['amount__avg'] or 0
    
    stats = {
        'total_earnings': abs(total_earnings),
        'total_spendings': abs(total_spendings),
        'avg_earnings': abs(avg_earnings),
        'avg_spendings': abs(avg_spendings),
        'has_earnings': earnings.exists(),
        'has_spendings': spendings.exists(),
    }

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.userprofile)
    
    return render(request, 'main/profile.html', {
        'form': form,
        'user': request.user,
        'transactions': transactions.order_by('-created_at')[:5],  # Show only last 5 transactions
        'stats': stats,
    })

# Map Page
def map_view(request):
    return render(request, 'main/map.html')

# Transactions Page
@login_required
def transactions(request):
    transaction_type = request.GET.get('type', 'all')
    
    # Base query
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate statistics
    earnings = transactions.filter(amount__gt=0)
    spendings = transactions.filter(amount__lt=0)
    
    # Calculate totals (handle None cases)
    total_earnings = earnings.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spendings = spendings.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate averages (handle None cases)
    avg_earnings = earnings.aggregate(Avg('amount'))['amount__avg'] or 0
    avg_spendings = spendings.aggregate(Avg('amount'))['amount__avg'] or 0
    
    stats = {
        'total_earnings': abs(total_earnings),
        'total_spendings': abs(total_spendings),
        'avg_earnings': abs(avg_earnings),
        'avg_spendings': abs(avg_spendings),
    }
    
    # Filter based on type
    if transaction_type == 'earnings':
        transactions = earnings
    elif transaction_type == 'spendings':
        transactions = spendings
    
    transactions = transactions.order_by('-created_at')
    
    return render(request, 'main/transactions.html', {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'stats': stats,
        'has_earnings': earnings.exists(),
        'has_spendings': spendings.exists(),
    })
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Create the user first
                    user = form.save()
                    
                    # Check if profile already exists
                    if not UserProfile.objects.filter(user=user).exists():
                        # Create the profile
                        profile = profile_form.save(commit=False)
                        profile.user = user
                        profile.save()
                    
                    username = form.cleaned_data.get('username')
                    messages.success(request, f'Account created for {username}!')
                    return redirect('login')
                    
            except IntegrityError as e:
                messages.error(request, f'Database error: {str(e)}')
                if 'user' in locals():
                    user.delete()
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                if 'user' in locals():
                    user.delete()
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    
    context = {
        'form': form,
        'profile_form': profile_form
    }
    
    return render(request, 'registration/signup.html', context)

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
    sort = request.GET.get('sort', '-date')
    if sort == 'price_low':
        rides = rides.order_by('amount')
    elif sort == 'price_high':
        rides = rides.order_by('-amount')
    else:
        rides = rides.order_by('-date', '-time')

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

@login_required
def driver_application(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = DriverApplicationForm(request.POST, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_driver = True
            profile.driver_status = 'pending'
            profile.save()
            messages.success(request, 'Your driver application has been submitted!')
            return redirect('profile')
    else:
        form = DriverApplicationForm(instance=user_profile)
    
    return render(request, 'main/driver_application.html', {'form': form})

@login_required
def request_ride(request):
    if request.method == 'POST':
        # Add your ride request logic here
        return redirect('find_ride')
    return render(request, 'main/find_ride.html')

@login_required
def accept_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    if ride.status != 'available':
        messages.error(request, 'This ride is no longer available.')
        return redirect('find_ride')
    
    if ride.driver == request.user:
        messages.error(request, 'You cannot accept your own ride.')
        return redirect('find_ride')
    
    ride.passenger = request.user
    ride.status = 'accepted'
    ride.save()
    
    # Create transaction for passenger (negative amount for spending)
    Transaction.objects.create(
        user=request.user,  # passenger
        amount=-ride.price,  # negative amount for spending
        description=f'Ride from {ride.pickup_location} to {ride.dropoff_location}',
        pickup_location=ride.pickup_location,
        dropoff_location=ride.dropoff_location
    )
    
    # Create transaction for driver (positive amount for earning)
    Transaction.objects.create(
        user=ride.driver,  # driver
        amount=ride.price,  # positive amount for earning
        description=f'Ride from {ride.pickup_location} to {ride.dropoff_location}',
        pickup_location=ride.pickup_location,
        dropoff_location=ride.dropoff_location
    )
    
    messages.success(request, 'Ride accepted successfully!')
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
            
            # If the user is a driver, they're creating a ride offer
            if request.user.userprofile.is_driver:
                ride.driver = request.user
                ride.status = 'available'
            else:
                # If the user is a passenger, they're requesting a ride
                ride.passenger = request.user
                ride.status = 'pending'
            
            ride.save()
            messages.success(request, 'Ride created successfully!')
            return redirect('rides')
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
            ).order_by('-date', '-time')
            return render(request, 'main/search_results.html', {'rides': rides})
    else:
        form = RideSearchForm()
    return render(request, 'main/search_rides.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save the user yet
            user.save()  # Now save the user
            
            # Create the UserProfile with location
            UserProfile.objects.create(
                user=user,
                location=form.cleaned_data.get('location', '')
            )
            
            # Log the user in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def current_journey(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Only allow access to the driver and passenger of this ride
    if request.user != ride.driver and request.user != ride.passenger:
        messages.error(request, 'You do not have permission to view this journey.')
        return redirect('home')
    
    # Only show active rides
    if ride.status != 'accepted':
        messages.error(request, 'This ride is not currently active.')
        return redirect('home')
    
    return render(request, 'main/current_journey.html', {
        'ride': ride
    })