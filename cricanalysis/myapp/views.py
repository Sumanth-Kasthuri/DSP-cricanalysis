from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm

# Create your views here.
def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if 'update-profile-form' in request.POST:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            # Update the user's profile fields
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if email:
                user.email = email

            # Save the updated user object
            user.save()
            messages.success(request, 'Profile updated successfully.', extra_tags='account-settings')

        elif 'change-password-form' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.', extra_tags='security')
            elif new_password != confirm_password:
                messages.error(request, 'New password and confirm password do not match.', extra_tags='security')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.', extra_tags='security')
            elif new_password.isdigit():
                messages.error(request, 'Password must contain at least one letter.', extra_tags='security')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  
                messages.success(request, "Password changed successfully.", extra_tags='security')

    return render(request, 'profile.html')

def matches_view(request):
    return render(request, 'matches.html')

def teams_views(request):
    return render(request, 'teams.html')

def players_view(request):
    return render(request, 'players.html')