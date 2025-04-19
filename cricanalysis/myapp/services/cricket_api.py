import requests

# Original API credentials (keeping for reference)
API_KEY = '17af6b8a-2fd9-45df-be74-b72634b69e1b'
BASE_URL = 'https://cricapi.com/api/cricket'

# RapidAPI credentials
RAPID_API_KEY = '80a106c916mshbc28c87b8a1145fp1317a1jsn9fc2ec8c94ec'
RAPID_API_HOST = 'cricbuzz-cricket.p.rapidapi.com'

def get_upcoming_matches():
    """
    Fetches all upcoming cricket matches from the API
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch upcoming matches: {response.status_code}"}

def get_recent_matches():
    """
    Fetches all recently completed cricket matches from the API
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch recent matches: {response.status_code}"}

def get_live_matches():
    """
    Fetches all currently live cricket matches from the API
    """
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Since we're now using the correct live matches endpoint,
        # no additional filtering should be needed
        return data
    else:
        return {"error": f"Failed to fetch live matches: {response.status_code}"}

def get_matches():
    """
    Fetches all cricket matches (upcoming, recent, and live)
    """
    upcoming = get_upcoming_matches()
    recent = get_recent_matches()
    live = get_live_matches()
    
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
            # Take only the first result for each name
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