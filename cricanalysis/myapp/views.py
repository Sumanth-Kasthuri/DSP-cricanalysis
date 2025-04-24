from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .services.cricket_api import *
from .services.weather_api import get_weather_for_venue
from django.http import HttpResponse
import requests
from django.views.decorators.cache import cache_page


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
                match_score = match.get("matchScore", {})  # may not exist

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
                    "matchId": match_info.get("matchId", "")  # Add matchId to the data
                })
    return matches

def matches_view(request):
    # Fetch match data from API services
    live_data = get_live_matches()
    upcoming_data = get_upcoming_matches()
    recent_data = get_recent_matches()
    
    # Process each type of match data
    live_matches = extract_matches(live_data)
    upcoming_matches = extract_matches(upcoming_data)
    recent_matches = extract_matches(recent_data)
    
    # Pass the processed data to the template
    return render(request, 'matches.html', {
        'live_matches': live_matches,
        'upcoming_matches': upcoming_matches,
        'recent_matches': recent_matches,
    })

def teams_views(request):
    # Fetch only international team data from API
    international_teams_data = get_international_teams()
    
    # Extract teams from API response
    all_teams = international_teams_data.get("list", [])
    
    return render(request, 'teams.html', {
        'teams': all_teams
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
    
    # Organize players alphabetically if on initial load
    if not search_query:
        players.sort(key=lambda x: x.get('name', ''))
    
    context = {
        'players': players,
        'search_query': search_query
    }
    
    return render(request, 'players.html', context)

def player_info_view(request):
    player_id = request.GET.get('id')
    stat_type = request.GET.get('type', 'info')  # Default to info instead of batting
    
    if not player_id:
        # No player ID provided
        return render(request, 'player_info.html', {'error': 'No player selected'})
    
    # Get player details
    player_details = get_player_details(player_id)
    
    # Initialize stats as None
    
    stats = None
    
    # Get stats based on selected type
    if stat_type == 'bowling':
        stats = get_player_bowling_stats(player_id)
    elif stat_type == 'batting':
        stats = get_player_batting_stats(player_id)
    # For 'info', we already have the player_details
    
    context = {
        'player_id': player_id,
        'player_details': player_details,
        'stats': stats,
        'stat_type': stat_type
    }
    
    return render(request, 'player_info.html', context)

@cache_page(60 * 60 * 24)  # Cache for 24 hours
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

def match_info_view(request):
    match_id = request.GET.get('id')
    
    if not match_id:
        # No match ID provided
        return render(request, 'match_info.html', {'error': 'No match selected'})
    
    # First, get the detailed match data to ensure we have venue, teams, and scores
    match_details = None
    
    # Check in live matches
    live_data = get_live_matches()
    live_matches = extract_matches(live_data)
    for match in live_matches:
        if str(match.get('matchId')) == str(match_id):
            match_details = match
            break
    
    # If not found in live, check in upcoming
    if not match_details:
        upcoming_data = get_upcoming_matches()
        upcoming_matches = extract_matches(upcoming_data)
        for match in upcoming_matches:
            if str(match.get('matchId')) == str(match_id):
                match_details = match
                break
    
    # If not found in upcoming, check in recent
    if not match_details:
        recent_data = get_recent_matches()
        recent_matches = extract_matches(recent_data)
        for match in recent_matches:
            if str(match.get('matchId')) == str(match_id):
                match_details = match
                break
    
    # Get match scorecard data
    scorecard_data = get_match_scorecard(match_id)
    
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
            'team2_score': match_details.get('team2_score', {}) if match_details else {}
        },
        'weather_data': weather_data
    }
    
    return render(request, 'match_info.html', context)

def team_info_view(request):
    team_id = request.GET.get('id')
    team_name = request.GET.get('team_name')
    tab = request.GET.get('tab', 'schedule')  # Default to schedule tab
    
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
    
    # Get players data for the team (whether we have team_id from URL or found it from team_name)
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
    
    # Initialize tab_data as empty
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