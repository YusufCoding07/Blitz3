from .models import UserProfile  # Update this if it exists

def user_profile(request):
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return {'user_profile': profile}
    return {'user_profile': None} 