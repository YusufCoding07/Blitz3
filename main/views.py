from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'main/home.html')

@login_required
def profile(request):
    return render(request, 'main/profile.html')
