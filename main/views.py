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
