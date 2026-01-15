"""
Weather API module - Handles all API interactions
"""

import requests
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import API_URL, API_KEY


def fetch_weather_data(city):
    """
    Fetch weather data from OpenWeatherMap API.
    
    Args:
        city (str): City name to fetch weather for
    
    Returns:
        dict: Weather data if successful, None if error occurs
    
    Raises:
        Prints error message to console
    """
    try:
        url = f'{API_URL}?q={city}&appid={API_KEY}'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Connection failed")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred - {e}")
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def parse_weather_data(data):
    """
    Parse weather data from API response.
    
    Args:
        data (dict): Raw API response data
    
    Returns:
        dict: Parsed weather information with keys:
              - weather_condition: Main weather condition
              - description: Weather description
              - temperature: Temperature in Celsius
              - pressure: Atmospheric pressure
              - humidity: Humidity percentage
        
        Returns None if parsing fails
    """
    try:
        return {
            'weather_condition': data['weather'][0]['main'],
            'description': data['weather'][0]['description'],
            'temperature': int(data['main']['temp'] - 273.15),
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity']
        }
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error parsing weather data: {e}")
        return None


def get_weather_info(city):
    """
    High-level function to fetch and parse weather information.
    
    Args:
        city (str): City name
    
    Returns:
        dict: Parsed weather data or None if error occurs
    """
    if not city or not city.strip():
        return None
    
    data = fetch_weather_data(city.strip())
    if data is None:
        return None
    
    return parse_weather_data(data)