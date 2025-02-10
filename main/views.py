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

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})