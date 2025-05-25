import requests
import time
import random


# RapidAPI credentials
RAPID_API_KEY = '80a106c916mshbc28c87b8a1145fp1317a1jsn9fc2ec8c94ec'
RAPID_API_HOST = 'cricbuzz-cricket.p.rapidapi.com'

def get_upcoming_matches(force_refresh=False):
    """
    Fetches all upcoming cricket matches from the API
    
    Args:
        force_refresh (bool): If True, adds a cache-busting parameter to ensure fresh data
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    # cache-busting parameter
    params = {}
    if force_refresh:
        params['_'] = int(time.time() * 1000) + random.randint(1, 1000)
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch upcoming matches: {response.status_code}"}

def get_recent_matches(force_refresh=False):
    """
    Fetches all recently completed cricket matches from the API
    
    Args:
        force_refresh (bool): If True, adds a cache-busting parameter to ensure fresh data
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    # cache-busting parameter
    params = {}
    if force_refresh:
        params['_'] = int(time.time() * 1000) + random.randint(1, 1000)
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch recent matches: {response.status_code}"}

def get_live_matches(force_refresh=False):
    """
    Fetches all currently live cricket matches from the API
    
    Args:
        force_refresh (bool): If True, adds a cache-busting parameter to ensure fresh data
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    # cache-busting parameter
    params = {}
    if force_refresh:
        params['_'] = int(time.time() * 1000) + random.randint(1, 1000)
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {"error": f"Failed to fetch live matches: {response.status_code}"}

def get_matches(force_refresh=False):
    """
    Fetches all cricket matches (upcoming, recent, and live)
    
    Args:
        force_refresh (bool): If True, adds a cache-busting parameter to ensure fresh data
    """
    upcoming = get_upcoming_matches(force_refresh)
    recent = get_recent_matches(force_refresh)
    live = get_live_matches(force_refresh)
    
    return {
        "upcoming": upcoming,
        "recent": recent,
        "live": live
    }

def get_international_teams():
    """
    Fetches all international teams from the API
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/international"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch international teams: {response.status_code}"}
    
def get_league_teams():
    """
    Fetches all domestic teams from the API
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/league"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch domestic teams: {response.status_code}"}

def search_players(player_name):
    """
    Searches for players by name
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    params = {
        "plrN": player_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to search players: {response.status_code}"}

def get_popular_players():
    """
    Returns a list of popular players (hardcoded for initial display)
    """
    popular_names = [
        "Virat Kohli", "Joe Root", "Steve Smith", "Kane Williamson", 
        "Babar Azam", "Ben Stokes", "Rohit Sharma", "Pat Cummins",
        "Jasprit Bumrah", "Shakib Al Hasan", "MS Dhoni", "AB de Villiers"
    ]
    
    all_players = []
    for name in popular_names:
        result = search_players(name)
        if "player" in result and result["player"]:
            all_players.append(result["player"][0])
    
    return {"player": all_players}

def get_player_details(player_id):
    """
    Get basic player details
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch player details: {response.status_code}"}

def get_player_batting_stats(player_id):
    """
    Get player batting statistics
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch batting stats: {response.status_code}"}

def get_player_bowling_stats(player_id):
    """
    Get player bowling statistics
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch bowling stats: {response.status_code}"}

def get_match_scorecard(match_id, force_refresh=False):
    """
    Get detailed scorecard for a specific match
    
    Args:
        match_id (str): ID of the match
        force_refresh (bool): If True, adds a cache-busting parameter to ensure fresh data
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    # cache-busting parameter
    params = {}
    if force_refresh:
        params['_'] = int(time.time() * 1000) + random.randint(1, 1000)
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch match scorecard: {response.status_code}"}

def get_team_schedule(team_id):
    """
    Get schedule of matches for a specific team
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/schedule"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch team schedule: {response.status_code}"}

def get_team_players(team_id):
    """
    Get players for a specific team
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/players"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch team players: {response.status_code}"}