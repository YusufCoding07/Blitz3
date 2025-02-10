from django.shortcuts import render

# Home Page (Find Ride)
def home(request):
    return render(request, 'main/home.html')

# Profile Page
def profile(request):
    return render(request, 'main/profile.html')

# Map Page
def map_view(request):
    return render(request, 'main/map.html')

def transactions(request):
    transactions = Transaction.objects.filter(user=request.user)  # Example query
    return render(request, 'main/transactions.html', {'transactions': transactions})

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html')

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')

from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    user_profile = request.user.profile  # Access the profile
    return render(request, 'main/profile.html', {'profile': user_profile})