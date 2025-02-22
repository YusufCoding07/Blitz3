from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Avg
from django.db import transaction, IntegrityError
from decimal import Decimal
from datetime import datetime

from .models import Transaction, UserProfile, Ride
from .forms import (
    UserRegisterForm,
    UserProfileForm,
    DriverApplicationForm,
    RideCreateForm,
    RideSearchForm,
    SignUpForm,
    ProfileUpdateForm
)

import logging
logger = logging.getLogger('django')
