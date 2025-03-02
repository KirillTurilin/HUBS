from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration process
    path('register/', views.register_view, name='registration_step1'),
    path('registration/personal-info/', views.registration_step2_view, name='registration_step2'),
    path('registration/profile-picture/', views.registration_step3_view, name='registration_step3'),
    
    # Home and profile
    path('', views.home_view, name='home'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Settings
    path('toggle-theme/', views.toggle_theme_view, name='toggle_theme'),
] 