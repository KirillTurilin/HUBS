from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse

from .models import User
from .forms import (
    CustomLoginForm, RegistrationStep1Form, RegistrationStep2Form, 
    RegistrationStep3Form, ProfileEditForm
)

class CustomLoginView(LoginView):
    """Custom login view with form validation"""
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        """Redirect to the appropriate page after login"""
        user = self.request.user
        if not user.registration_complete:
            # Continue the registration process
            if user.registration_step == 1:
                return reverse('registration_step2')
            elif user.registration_step == 2:
                return reverse('registration_step3')
            elif user.registration_step == 3:
                # Mark registration as complete and proceed
                user.registration_step = 4
                user.save()
        return reverse('home')
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - if user is authenticated, redirect to home"""
        if request.user.is_authenticated and request.user.registration_complete:
            return redirect('home')
        return super().get(request, *args, **kwargs)

def register_view(request):
    """First step of registration - basic account info"""
    if request.user.is_authenticated and request.user.registration_complete:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationStep1Form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.registration_step = 2
            user.save()
            login(request, user)
            return redirect('registration_step2')
    else:
        form = RegistrationStep1Form()
    
    return render(request, 'accounts/registration_step1.html', {'form': form})

@login_required
def registration_step2_view(request):
    """Second step of registration - personal information"""
    user = request.user
    
    # Make sure the user is on the correct registration step
    if user.registration_step > 2 and user.registration_complete:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationStep2Form(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.registration_step = 3
            user.save()
            return redirect('registration_step3')
    else:
        form = RegistrationStep2Form(instance=user)
    
    return render(request, 'accounts/registration_step2.html', {'form': form})

@login_required
def registration_step3_view(request):
    """Third step of registration - avatar upload"""
    user = request.user
    
    # Make sure the user is on the correct registration step
    if user.registration_step > 3 and user.registration_complete:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationStep3Form(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.registration_step = 4  # Registration complete
            user.save()
            return redirect('home')
    else:
        form = RegistrationStep3Form(instance=user)
    
    return render(request, 'accounts/registration_step3.html', {'form': form})

@login_required
def home_view(request):
    """Home view - redirects to the appropriate main section"""
    # If registration is not complete, redirect to the appropriate step
    if not request.user.registration_complete:
        if request.user.registration_step == 1:
            return redirect('registration_step1')
        elif request.user.registration_step == 2:
            return redirect('registration_step2')
        elif request.user.registration_step == 3:
            return redirect('registration_step3')
    
    # Default to messenger as the main section
    return redirect('messenger:chat_list')

@login_required
def profile_view(request, username):
    """View for displaying user profiles"""
    user = get_object_or_404(User, username=username)
    is_own_profile = request.user == user
    
    context = {
        'profile_user': user,
        'is_own_profile': is_own_profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    """View for editing user profile"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def toggle_theme_view(request):
    """Toggle between light and dark mode"""
    if request.method == 'POST':
        user = request.user
        user.dark_mode = not user.dark_mode
        user.save()
        
        return JsonResponse({'status': 'success', 'dark_mode': user.dark_mode})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400) 