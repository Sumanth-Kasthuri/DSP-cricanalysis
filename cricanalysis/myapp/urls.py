from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    # Add more URL patterns as needed
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('matches/', views.matches_view, name='matches'),
    path('teams/', views.teams_views, name='teams'),
    path('players/', views.players_view, name='players'),
    path('profile/', views.profile_view, name='profile'),
    path('player_info/', views.player_info_view, name='player_info'),
    path('player_image/', views.player_image_proxy, name='player_image'),
]