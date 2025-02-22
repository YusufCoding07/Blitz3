from django.db.models import Sum, Avg  # Ensure this import exists
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile, Transaction
from .forms import ProfileUpdateForm

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    # Get or create UserProfile for the user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get transactions for the user
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate earnings and spendings
    earnings = transactions.filter(amount__gt=0)
    spendings = transactions.filter(amount__lt=0)
    
    # Calculate totals (handle None cases)
    total_earnings = earnings.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spendings = spendings.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate averages
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
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user_profile)
    
    return render(request, 'main/profile.html', {
        'form': form,
        'user': request.user,
        'transactions': transactions.order_by('-created_at')[:5],
        'stats': stats,
    })
    
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
