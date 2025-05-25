from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .models import FavoriteTeam
from .services.cricket_api import *
from .services.weather_api import get_weather_for_venue
from .services.prediction_service import predict_match_outcome, format_prediction_for_display, train_models
from django.http import HttpResponse
import requests
from django.views.decorators.cache import cache_page
import time


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
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            # Update the user's profile fields
            if username:
                user.username = username
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
                
        elif 'delete-account-form' in request.POST:
            # Delete the user's account
            user.delete()
            # Log the user out
            logout(request)
            # Redirect to home page with a message
            messages.success(request, 'Your account has been successfully deleted.')
            return redirect('home')

    return render(request, 'profile.html')

def extract_matches(match_type_data):
    matches = []

    for match_group in match_type_data.get("typeMatches", []):
        for series in match_group.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper")
            if not wrapper:
                continue
            series_name = wrapper.get("seriesName", "")
            for match in wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})
                team1 = match_info.get("team1", {})
                team2 = match_info.get("team2", {})
                venue = match_info.get("venueInfo", {})
                match_score = match.get("matchScore", {})  

                team1_score = match_score.get("team1Score", {}).get("inngs1", {})
                team2_score = match_score.get("team2Score", {}).get("inngs1", {})

                matches.append({
                    "seriesName": series_name,
                    "team1": team1,
                    "team2": team2,
                    "venue": venue,
                    "status": match_info.get("status", ""),
                    "matchFormat": match_info.get("matchFormat", ""),
                    "matchDesc": match_info.get("matchDesc", ""),
                    "stateTitle": match_info.get("stateTitle", ""),
                    "team1_score": team1_score,
                    "team2_score": team2_score,
                    "startDate": match_info.get("startDate", ""),
                    "matchId": match_info.get("matchId", "")  
                })
    return matches

# Update matches_view to include user's favorite teams
def matches_view(request):
    # Fetch match data from API services with force_refresh
    live_data = get_live_matches(force_refresh=True)
    upcoming_data = get_upcoming_matches(force_refresh=True)
    recent_data = get_recent_matches(force_refresh=True)
    
    # Process each type of match data
    live_matches = extract_matches(live_data)
    upcoming_matches = extract_matches(upcoming_data)
    recent_matches = extract_matches(recent_data)
    
    # Get user's favorite teams if logged in
    favorite_team_ids = []
    if request.user.is_authenticated:
        favorite_team_ids = list(FavoriteTeam.objects.filter(
            user=request.user).values_list('team_id', flat=True))
    
    # timestamp to prevent browser caching
    timestamp = int(time.time())
    
    # Pass the processed data to the template
    return render(request, 'matches.html', {
        'live_matches': live_matches,
        'upcoming_matches': upcoming_matches,
        'recent_matches': recent_matches,
        'favorite_team_ids': favorite_team_ids,
        'timestamp': timestamp,
    })

def teams_views(request):
    # Fetch only international team data from API
    international_teams_data = get_international_teams()
    
    # Extract teams from API response
    all_teams = international_teams_data.get("list", [])
    
    # Get user's favorite teams if logged in
    favorite_team_ids = []
    if request.user.is_authenticated:
        favorite_team_ids = list(FavoriteTeam.objects.filter(
            user=request.user).values_list('team_id', flat=True))
    
    return render(request, 'teams.html', {
        'teams': all_teams,
        'favorite_team_ids': favorite_team_ids
    })

def players_view(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        # If search query provided, search for players
        player_data = search_players(search_query)
    else:
        # Otherwise, show some popular players
        player_data = get_popular_players()
    
    players = player_data.get('player', [])
    
    # Organise players alphabetically if on initial load
    if not search_query:
        players.sort(key=lambda x: x.get('name', ''))
    
    context = {
        'players': players,
        'search_query': search_query
    }
    
    return render(request, 'players.html', context)

def player_info_view(request):
    player_id = request.GET.get('id')
    stat_type = request.GET.get('type', 'info')  
    
    if not player_id:
        # No player ID provided
        return render(request, 'player_info.html', {'error': 'No player selected'})
    
    # Get player details
    player_details = get_player_details(player_id)
    
    # Initialise stats as None
    
    stats = None
    
    # Get stats based on selected type
    if stat_type == 'bowling':
        stats = get_player_bowling_stats(player_id)
    elif stat_type == 'batting':
        stats = get_player_batting_stats(player_id)
    
    context = {
        'player_id': player_id,
        'player_details': player_details,
        'stats': stats,
        'stat_type': stat_type
    }
    
    return render(request, 'player_info.html', context)

@cache_page(60 * 60 * 24) 
def player_image_proxy(request):
    """
    Proxy view that fetches player images from the API and serves them
    """
    image_id = request.GET.get('id')
    if not image_id:
        # Return a placeholder image or 404
        return HttpResponse(status=404)
    
    url = f"https://cricbuzz-cricket.p.rapidapi.com/img/v1/i1/c{image_id}/i.jpg"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Return the image with correct content type
            return HttpResponse(
                content=response.content,
                content_type=response.headers.get('Content-Type', 'image/jpeg')
            )
        else:
            return HttpResponse(status=404)
    except Exception as e:
        return HttpResponse(status=500)
    
def is_ipl_team(team_name):
    """Check if a team is an IPL team"""
    ipl_teams = [
        'chennai super kings', 'delhi capitals', 'gujarat titans', 
        'kolkata knight riders', 'lucknow super giants', 'mumbai indians', 
        'punjab kings', 'rajasthan royals', 'royal challengers bangalore', 
        'sunrisers hyderabad'
    ]
    return team_name.lower() in ipl_teams

def match_info_view(request):
    match_id = request.GET.get('id')
    
    if not match_id:
        # No match ID provided
        return render(request, 'match_info.html', {'error': 'No match selected'})
    
    # First, get the detailed match data for venue, teams, and scores
    match_details = None
    is_finished = False
    
    # Check in live matches with force_refresh
    live_data = get_live_matches(force_refresh=True)
    live_matches = extract_matches(live_data)
    for match in live_matches:
        if str(match.get('matchId')) == str(match_id):
            match_details = match
            break
    
    # If not found in live, check in upcoming with force_refresh
    if not match_details:
        upcoming_data = get_upcoming_matches(force_refresh=True)
        upcoming_matches = extract_matches(upcoming_data)
        for match in upcoming_matches:
            if str(match.get('matchId')) == str(match_id):
                match_details = match
                break
    
    # If not found in upcoming, check in recent with force_refresh=True
    if not match_details:
        recent_data = get_recent_matches(force_refresh=True)
        recent_matches = extract_matches(recent_data)
        for match in recent_matches:
            if str(match.get('matchId')) == str(match_id):
                match_details = match
                is_finished = True  
                break
    
    # Get match scorecard data with force_refresh
    scorecard_data = get_match_scorecard(match_id, force_refresh=True)
    
    # Check for errors in the API response
    if 'error' in scorecard_data:
        return render(request, 'match_info.html', {'error': scorecard_data['error']})
    
    # Create venue string for the match
    venue_str = None
    if match_details and 'venue' in match_details:
        if isinstance(match_details['venue'], dict):
            venue_str = match_details['venue'].get('ground', '') + ', ' + match_details['venue'].get('city', '')
        else:
            venue_str = match_details.get('venue', '')
    else:
        venue_str = scorecard_data.get('venue', 'Unknown Venue')
    
    # Get weather information for the venue
    weather_data = get_weather_for_venue(venue_str)
    
    # Check if match is in second innings with scores
    is_second_innings = False
    if match_details and match_details.get('team1_score') and match_details.get('team2_score'):
        is_second_innings = True
    
    # Prepare match prediction if we have team information AND the match is not finished
    prediction_data = {}
    if match_details and 'team1' in match_details and 'team2' in match_details and not is_finished:
        team1_name = match_details['team1'].get('teamName')
        team2_name = match_details['team2'].get('teamName')
        
        # Determine match format - check if these are IPL teams
        match_format = match_details.get('matchFormat', 'ODI')
        
        # Override the match format to IPL if these are IPL teams
        if team1_name and team2_name and (is_ipl_team(team1_name) or is_ipl_team(team2_name)):
            match_format = 'IPL'
            print(f"Detected IPL teams: {team1_name} vs {team2_name}, using IPL model")
        
        # Get prediction - include match details for potential live predictions in second innings
        if team1_name and team2_name:
            # Prepare the match details object with necessary information for live prediction
            prediction_match_details = {
                'match_format': match_format,
                'team1_name': team1_name,
                'team2_name': team2_name,
                'team1_score': {},
                'team2_score': {}
            }
            
            # Format team scores for live prediction if they exist
            if match_details.get('team1_score'):
                team1_score = match_details.get('team1_score', {})
                prediction_match_details['team1_score'] = {
                    'runs': team1_score.get('runs'),
                    'wickets': team1_score.get('wickets'),
                    'overs': team1_score.get('overs')
                }
                
            if match_details.get('team2_score'):
                team2_score = match_details.get('team2_score', {})
                prediction_match_details['team2_score'] = {
                    'runs': team2_score.get('runs'),
                    'wickets': team2_score.get('wickets'),
                    'overs': team2_score.get('overs')
                }
            
            # Get prediction with match details for live prediction during second innings
            raw_prediction = predict_match_outcome(team1_name, team2_name, match_format, prediction_match_details)
            prediction_data = format_prediction_for_display(raw_prediction, team1_name, team2_name)
    
    # Add timestamp to prevent browser caching
    timestamp = int(time.time())
    
    # Prepare context for the template with enhanced details
    context = {
        'match_id': match_id,
        'scoreCard': scorecard_data.get('scoreCard', []),
        'match_details': {
            'matchDescription': match_details.get('matchDesc') if match_details else scorecard_data.get('matchDescription', 'Cricket Match'),
            'venue': venue_str,
            'matchDate': scorecard_data.get('matchDate', ''),
            'status': match_details.get('status') if match_details else scorecard_data.get('status', ''),
            'team1': match_details.get('team1', {}) if match_details else {},
            'team2': match_details.get('team2', {}) if match_details else {},
            'team1_score': match_details.get('team1_score', {}) if match_details else {},
            'team2_score': match_details.get('team2_score', {}) if match_details else {},
            'matchFormat': match_details.get('matchFormat', '') if match_details else scorecard_data.get('matchFormat', '')
        },
        'weather_data': weather_data,
        'prediction': prediction_data,
        'is_finished': is_finished,
        'is_second_innings': is_second_innings,
        'timestamp': timestamp,
    }
    
    return render(request, 'match_info.html', context)

def team_info_view(request):
    team_id = request.GET.get('id')
    team_name = request.GET.get('team_name')
    tab = request.GET.get('tab', 'schedule')  
    
    if not team_id and not team_name:
        # No team ID or team name provided
        return render(request, 'team_info.html', {'error': 'No team selected'})
    
    # First, if we only have team_id but no team_name, fetch the team details from the international teams list
    if team_id and not team_name:
        international_teams_data = get_international_teams()
        all_teams = international_teams_data.get("list", [])
        
        # Find the team name that matches the provided team ID
        for team in all_teams:
            if str(team.get('teamId')) == str(team_id):
                team_name = team.get('teamName')
                team_sname = team.get('teamSName')
                # Create team details directly from this data
                team_details = {
                    'teamName': team_name,
                    'teamSName': team_sname
                }
                break
    
    # Get players data for the team 
    team_players_data = {}
    
    if team_id:
        team_players_data = get_team_players(team_id)
    elif team_name:
        # If we only have team_name, find the team_id first
        international_teams_data = get_international_teams()
        all_teams = international_teams_data.get("list", [])
        
        # Find the team ID that matches the provided team name
        for team in all_teams:
            if team.get('teamName') == team_name:
                team_id = team.get('teamId')
                team_details = {
                    'teamName': team_name,
                    'teamSName': team.get('teamSName', '')
                }
                break
        
        if team_id:
            team_players_data = get_team_players(team_id)
        else:
            return render(request, 'team_info.html', {'error': f'Team not found: {team_name}'})
    
    if 'error' in team_players_data:
        return render(request, 'team_info.html', {'error': team_players_data['error']})
    
    # If team_details wasn't set above, try to extract from the players data
    if not 'team_details' in locals() or not team_name:
        # Attempt to extract team name from team_players_data
        if 'teamName' in team_players_data:
            team_name = team_players_data['teamName']
        elif 'name' in team_players_data:
            team_name = team_players_data['name']
        
        team_details = {
            'teamName': team_name if team_name else "Team Name Not Found",
            'teamSName': team_players_data.get('teamSName', '')
        }
    
    # Initialise tab_data as empty
    tab_data = {}
    
    # Fetch data based on selected tab
    if tab == 'schedule':
        schedule_data = get_team_schedule(team_id)
        
        # Debug the schedule data to understand its structure better
        print("Schedule API Response Keys:", schedule_data.keys() if schedule_data else "No data")
        
        # Handle the schedule data - check if it contains "teamMatchesData" as per the API response
        if schedule_data and 'teamMatchesData' in schedule_data:
            # Return the full schedule data as is
            tab_data = schedule_data
        else:
            # If the expected structure is not found, provide an error
            tab_data = {
                'error': 'No schedule information available for this team'
            }
    elif tab == 'players':
        # For players tab, ensure we have the team name
        tab_data = {
            'player': team_players_data.get('player', []),
            'name': team_details['teamName']
        }
    
    context = {
        'team_id': team_id,
        'team_details': team_details,
        'tab': tab,
        'tab_data': tab_data
    }
    
    return render(request, 'team_info.html', context)

@login_required
def add_favorite_team(request):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        team_name = request.POST.get('team_name')
        team_sname = request.POST.get('team_sname', '')
        
        if not team_id or not team_name:
            return JsonResponse({'success': False, 'message': 'Team information is incomplete'})
        
        # Check if this team is already a favorite
        existing = FavoriteTeam.objects.filter(user=request.user, team_id=team_id).exists()
        if existing:
            return JsonResponse({'success': True, 'message': f'{team_name} is already in your favorites'})
        
        # Add the team to favorites
        favorite = FavoriteTeam(
            user=request.user,
            team_id=team_id,
            team_name=team_name,
            team_sname=team_sname
        )
        favorite.save()
        
        return JsonResponse({'success': True, 'message': f'{team_name} added to favorites'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def remove_favorite_team(request):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        
        if not team_id:
            return JsonResponse({'success': False, 'message': 'Team ID is required'})
        
        # Find and delete the favorite
        favorite = FavoriteTeam.objects.filter(user=request.user, team_id=team_id).first()
        if favorite:
            team_name = favorite.team_name
            favorite.delete()
            return JsonResponse({'success': True, 'message': f'{team_name} removed from favorites'})
        else:
            return JsonResponse({'success': True, 'message': 'Team is not in your favorites'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})