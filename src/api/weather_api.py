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


OPENMETEO_UV_URL = 'https://api.open-meteo.com/v1/forecast'


def fetch_uv_index_from_openmeteo(lat, lon):
    """
    Fetch real UV index from Open-Meteo API (free, no API key).
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        float: UV index value, or None if fetch fails
    """
    try:
        url = f'{OPENMETEO_UV_URL}?latitude={lat}&longitude={lon}&current=uv_index'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        result = response.json()
        uv = result.get('current', {}).get('uv_index')
        return float(uv) if uv is not None else None
    except Exception:
        return None


def uv_index_to_display(uv):
    """
    Format UV index for display: numeric value + WHO category.
    
    Args:
        uv: UV index (float) or None
    
    Returns:
        str: e.g. "5.2 (Moderate)" or "N/A"
    """
    if uv is None:
        return "N/A"
    uv = float(uv)
    if uv <= 2:
        cat = "Low"
    elif uv <= 5:
        cat = "Moderate"
    elif uv <= 7:
        cat = "High"
    elif uv <= 10:
        cat = "Very High"
    else:
        cat = "Extreme"
    return f"{uv:.1f} ({cat})"


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
              - sunrise: Sunrise time (Unix timestamp)
              - sunset: Sunset time (Unix timestamp)
              - visibility: Visibility in km
              - uv_index: UV index (real from Open-Meteo, or estimate fallback)
        
        Returns None if parsing fails
    """
    try:
        from datetime import datetime
        
        parsed = {
            'weather_condition': data['weather'][0]['main'],
            'description': data['weather'][0]['description'],
            'temperature': int(data['main']['temp'] - 273.15),
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity']
        }
        
        # Extract sunrise and sunset (Unix timestamps)
        if 'sys' in data:
            parsed['sunrise'] = data['sys'].get('sunrise')
            parsed['sunset'] = data['sys'].get('sunset')
            parsed['timezone'] = data.get('timezone', 0)  # Timezone offset in seconds
        
        # Extract visibility (in meters, convert to km)
        if 'visibility' in data:
            parsed['visibility'] = data['visibility'] / 1000.0  # Convert meters to km
        else:
            parsed['visibility'] = None
        
        # UV Index: fetch real data from Open-Meteo using lat/lon
        uv_display = "N/A"
        if 'coord' in data:
            lat = data['coord'].get('lat')
            lon = data['coord'].get('lon')
            if lat is not None and lon is not None:
                uv_value = fetch_uv_index_from_openmeteo(lat, lon)
                uv_display = uv_index_to_display(uv_value)
        if uv_display == "N/A":
            uv_display = calculate_uv_index_estimate(
                parsed.get('sunrise'),
                parsed.get('sunset'),
                parsed['weather_condition']
            )
        parsed['uv_index'] = uv_display
        
        return parsed
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error parsing weather data: {e}")
        return None


def calculate_uv_index_estimate(sunrise, sunset, weather_condition):
    """
    Estimate UV index based on time of day and weather conditions.
    This is a rough estimate - for accurate UV index, use One Call API 3.0.
    
    Args:
        sunrise: Sunrise Unix timestamp
        sunset: Sunset Unix timestamp
        weather_condition: Weather condition (Clear, Clouds, etc.)
    
    Returns:
        str: UV index category
    """
    from datetime import datetime
    
    if not sunrise or not sunset:
        return "N/A"
    
    now = datetime.now().timestamp()
    current_hour = datetime.now().hour
    
    # Check if it's daytime
    if sunrise <= now <= sunset:
        # Peak UV hours are typically 10 AM - 4 PM
        if 10 <= current_hour <= 16:
            # Clear sky = higher UV, Cloudy = lower UV
            if 'Clear' in weather_condition or 'Sun' in weather_condition:
                return "High (7-9)"
            elif 'Cloud' in weather_condition:
                return "Moderate (4-6)"
            else:
                return "Low (2-4)"
        elif 6 <= current_hour < 10 or 16 < current_hour <= 20:
            return "Moderate (3-5)"
        else:
            return "Low (1-3)"
    else:
        return "None (Night)"


def fetch_hourly_forecast(city):
    """
    Fetch hourly forecast data from OpenWeatherMap API (5-day/3-hour forecast).
    
    Args:
        city (str): City name to fetch forecast for
    
    Returns:
        dict: Forecast data if successful, None if error occurs
    """
    try:
        # Use forecast endpoint for hourly data
        forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'
        url = f'{forecast_url}?q={city}&appid={API_KEY}'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Error: Forecast request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Forecast connection failed")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: Forecast HTTP error occurred - {e}")
        return None
    except Exception as e:
        print(f"Error fetching forecast data: {e}")
        return None


def parse_hourly_forecast(forecast_data):
    """
    Parse hourly forecast data from API response.
    OpenWeatherMap returns 3-hour intervals, so we interpolate to get hourly data.
    
    Args:
        forecast_data (dict): Raw forecast API response
    
    Returns:
        list: List of hourly forecast entries (24 hours), each with:
              - time: Hour string (e.g., "14:00")
              - temperature: Temperature in Celsius
              - icon: Weather icon emoji
              - condition: Weather condition
    """
    try:
        from datetime import datetime, timezone, timedelta
        
        hourly_list = []
        
        if 'list' not in forecast_data or not forecast_data['list']:
            return hourly_list
        
        timezone_offset = forecast_data.get('city', {}).get('timezone', 0)
        tz = timezone(timedelta(seconds=timezone_offset))
        
        # Get forecast items (3-hour intervals, up to 24 hours = 8 items)
        forecast_items = forecast_data['list'][:8]
        
        if not forecast_items:
            return hourly_list
        
        # Parse all forecast points
        forecast_points = []
        for item in forecast_items:
            dt_timestamp = item['dt']
            dt_utc = datetime.fromtimestamp(dt_timestamp, tz=timezone.utc)
            dt_local = dt_utc.astimezone(tz)
            
            temp_kelvin = item['main']['temp']
            temp_celsius = temp_kelvin - 273.15
            
            weather_main = item['weather'][0]['main'].lower()
            weather_desc = item['weather'][0]['description'].lower()
            
            # Store condition string - UI will convert to PNG icon
            condition = item['weather'][0]['main']
            
            forecast_points.append({
                'datetime': dt_local,
                'temperature': temp_celsius,
                'condition': condition  # UI will load PNG icon based on condition
            })
        
        # Generate hourly data by interpolating between 3-hour intervals
        current_time = datetime.now(tz)
        current_hour = current_time.replace(minute=0, second=0, microsecond=0)
        
        for i in range(24):
            target_hour = current_hour + timedelta(hours=i)
            
            # Find the two forecast points that bracket this hour
            prev_point = None
            next_point = None
            
            for j, point in enumerate(forecast_points):
                if point['datetime'] <= target_hour:
                    prev_point = point
                    if j + 1 < len(forecast_points):
                        next_point = forecast_points[j + 1]
                else:
                    if not next_point:
                        next_point = point
                    break
            
            # If we only have one point (before or after), use it
            if prev_point and not next_point:
                temp = prev_point['temperature']
                icon = prev_point['icon']
            elif next_point and not prev_point:
                temp = next_point['temperature']
                icon = next_point['icon']
            elif prev_point and next_point:
                # Interpolate temperature between the two points
                time_diff = (next_point['datetime'] - prev_point['datetime']).total_seconds() / 3600.0
                if time_diff > 0:
                    hours_from_prev = (target_hour - prev_point['datetime']).total_seconds() / 3600.0
                    ratio = hours_from_prev / time_diff
                    temp = prev_point['temperature'] + (next_point['temperature'] - prev_point['temperature']) * ratio
                else:
                    temp = prev_point['temperature']
                
                # Use condition from the nearest point
                if hours_from_prev < time_diff / 2:
                    condition = prev_point['condition']
                else:
                    condition = next_point['condition']
            else:
                # Fallback if no points found
                temp = 20.0  # Default temperature
                condition = 'Unknown'
            
            hourly_list.append({
                'time': target_hour.strftime("%H:%M"),
                'hour': target_hour.hour,
                'temperature': temp,
                'condition': condition  # UI will load PNG icon based on condition
            })
        
        return hourly_list
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error parsing hourly forecast: {e}")
        import traceback
        traceback.print_exc()
        return []


def fetch_daily_forecast(lat, lon):
    """
    Fetch 15-day forecast from Open-Meteo API (free, no API key).
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict: Open-Meteo daily forecast data, or None if fetch fails
    """
    try:
        url = (
            f'{OPENMETEO_UV_URL}?latitude={lat}&longitude={lon}'
            '&daily=temperature_2m_max,temperature_2m_min,weathercode'
            '&forecast_days=15'
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def wmo_to_condition(code):
    """Map WMO weather code to condition string for icon lookup."""
    if code is None or code == 0:
        return 'clear'
    if code in (1, 2, 3):
        return 'clouds'
    if code in (45, 48):
        return 'fog'
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return 'rain'
    if code in (71, 73, 75, 77, 85, 86):
        return 'snow'
    if code in (95, 96, 99):
        return 'thunderstorm'
    if code in (52, 54):
        return 'drizzle'
    return 'clouds'


def parse_daily_forecast(openmeteo_data):
    """
    Parse 15-day forecast from Open-Meteo response.
    
    Args:
        openmeteo_data (dict): Raw Open-Meteo daily forecast response
    
    Returns:
        list: Up to 15 daily entries with: day (e.g. "Mon 27"), condition,
              temperature_min, temperature_max
    """
    from datetime import datetime
    
    result = []
    try:
        daily = openmeteo_data.get('daily', {})
        times = daily.get('time', [])
        max_t = daily.get('temperature_2m_max', [])
        min_t = daily.get('temperature_2m_min', [])
        codes = daily.get('weathercode', [])
        
        for i in range(min(15, len(times))):
            date_str = times[i]
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                day_label = dt.strftime('%a %d')  # "Mon 27"
            except Exception:
                day_label = date_str[:10] if len(date_str) >= 10 else date_str
            
            t_max = max_t[i] if i < len(max_t) else None
            t_min = min_t[i] if i < len(min_t) else None
            code = codes[i] if i < len(codes) else 0
            
            result.append({
                'day': day_label,
                'temperature_max': float(t_max) if t_max is not None else None,
                'temperature_min': float(t_min) if t_min is not None else None,
                'condition': wmo_to_condition(code),
            })
        return result
    except (KeyError, TypeError, IndexError) as e:
        print(f"Error parsing daily forecast: {e}")
        return []


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
    
    parsed = parse_weather_data(data)
    
    # Also fetch hourly forecast
    forecast_data = fetch_hourly_forecast(city.strip())
    if forecast_data:
        parsed['hourly_forecast'] = parse_hourly_forecast(forecast_data)
    else:
        parsed['hourly_forecast'] = []
    
    # Fetch 15-day forecast using lat/lon from current weather
    coord = data.get('coord', {})
    lat, lon = coord.get('lat'), coord.get('lon')
    if lat is not None and lon is not None:
        daily_data = fetch_daily_forecast(lat, lon)
        if daily_data:
            parsed['daily_forecast'] = parse_daily_forecast(daily_data)
        else:
            parsed['daily_forecast'] = []
    else:
        parsed['daily_forecast'] = []
    
    return parsed


def format_sunrise_sunset(timestamp, timezone_offset=0):
    """
    Format sunrise/sunset timestamp to readable time.
    
    Args:
        timestamp: Unix timestamp
        timezone_offset: Timezone offset in seconds (from UTC)
    
    Returns:
        str: Formatted time string (e.g., "6:45 AM")
    """
    from datetime import datetime, timezone, timedelta
    
    if not timestamp:
        return "N/A"
    
    try:
        # Create timezone-aware datetime from timestamp (UTC)
        dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        # Apply timezone offset
        tz = timezone(timedelta(seconds=timezone_offset))
        dt_local = dt_utc.astimezone(tz)
        
        # Format as 12-hour time
        formatted = dt_local.strftime("%I:%M %p")
        # Remove leading zero from hour if present
        if formatted.startswith('0'):
            formatted = formatted[1:]
        return formatted
    except Exception as e:
        print(f"Error formatting time: {e}")
        return "N/A"