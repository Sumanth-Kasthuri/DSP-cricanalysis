import requests

WEATHER_API_KEY = "111f566059e30834783cf82e971b6d34"

def extract_city_from_venue(venue_str):
    """
    Extracts city name from a venue string like 'M.Chinnaswamy Stadium, Bengaluru'
    
    Args:
        venue_str (str): The venue string containing the city
        
    Returns:
        str: The city name
    """
    if not venue_str:
        return None
    
    parts = venue_str.split(',')
    if len(parts) >= 2:
        # city is the last part after the last comma
        city = parts[-1].strip()
        return city
    
    return None

def get_weather_for_city(city_name):
    """
    Gets the current weather information for a city
    
    Args:
        city_name (str): Name of the city
        
    Returns:
        dict: Weather information for the city
    """
    if not city_name:
        return {"error": "No city name provided"}
    
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': WEATHER_API_KEY,
        'units': 'metric'  
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant weather information
            weather_info = {
                'temperature': data.get('main', {}).get('temp'),
                'feels_like': data.get('main', {}).get('feels_like'),
                'humidity': data.get('main', {}).get('humidity'),
                'description': data.get('weather', [{}])[0].get('description', ''),
                'icon': data.get('weather', [{}])[0].get('icon', ''),
                'wind_speed': data.get('wind', {}).get('speed'),
                'city_name': data.get('name'),
                'timestamp': data.get('dt')
            }
            
            return weather_info
        else:
            return {"error": f"Failed to fetch weather: {response.status_code}"}
    except Exception as e:
        return {"error": f"Error fetching weather data: {str(e)}"}

def get_weather_for_venue(venue_str):
    """
    Gets weather for a cricket venue by extracting the city name and fetching weather
    
    Args:
        venue_str (str): The venue string (e.g. 'M.Chinnaswamy Stadium, Bengaluru')
        
    Returns:
        dict: Weather information for the venue's city
    """
    city = extract_city_from_venue(venue_str)
    if not city:
        return {"error": "Could not extract city from venue"}
    
    return get_weather_for_city(city)