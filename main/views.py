# main/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')  # Directly render your template
def profile(request):
    return render(request, 'main/profile.html')
