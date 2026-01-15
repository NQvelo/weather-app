
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Callable

# Add parent directories to path to import from api folder
current_dir = Path(__file__).parent
src_dir = current_dir.parent
project_root = src_dir.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

# Import API module from weather_api
from api.weather_api import get_weather_info

class WeatherController:
    def __init__(self):
        self.current_weather_data = None
        self.current_city = None
        self.callbacks = {
            'on_success': None,
            'on_error': None,
            'on_loading': None
        }
    
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register callback functions for GUI updates
        
        Args:
            event: Event name ('on_success', 'on_error', 'on_loading')
            callback: Function to call when event occurs
        """
        if event in self.callbacks:
            self.callbacks[event] = callback
            print(f"✅ Registered callback: {event}")
    
    def _trigger_callback(self, event: str, *args, **kwargs):
        """Trigger a registered callback"""
        if self.callbacks.get(event):
            self.callbacks[event](*args, **kwargs)
    
    # ==================== Weather Data Fetching ====================
    
    def fetch_weather(self, city: str) -> bool:
        """
        Fetch weather data for a given city using Group 1's API
        
        Args:
            city: City name to fetch weather for
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"\n🌤️  Controller: Fetching weather for '{city}'...")
        
        # Validate input
        is_valid, error_msg = self.validate_city_input(city)
        if not is_valid:
            print(f"❌ Validation failed: {error_msg}")
            self._trigger_callback('on_error', "Invalid Input", error_msg)
            return False
        
        # Trigger loading state
        self._trigger_callback('on_loading', True, f"Fetching weather for {city}...")
        
        try:
            # Call Group 1's API function
            print(f"📡 Calling API: get_weather_info('{city}')")
            weather_data = get_weather_info(city)
            
            if weather_data is None:
                print(f"❌ API returned None for '{city}'")
                self._trigger_callback('on_error', 
                                     "No Data", 
                                     f"Could not fetch weather data for '{city}'. Please check the city name.")
                self._trigger_callback('on_loading', False, "")
                return False
            
            print(f"✅ API returned data: {weather_data}")
            
            # Store current data
            self.current_weather_data = weather_data
            self.current_city = city
            
            # Process data for GUI display
            processed_data = self._process_weather_data(weather_data, city)
            print(f"✅ Processed data: {processed_data}")
            
            # Trigger success callback
            self._trigger_callback('on_success', processed_data)
            self._trigger_callback('on_loading', False, "")
            
            return True
            
        except Exception as e:
            # Handle unexpected errors
            print(f"❌ Exception occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            
            self._trigger_callback('on_error', 
                                 "Error", 
                                 f"An unexpected error occurred: {str(e)}")
            self._trigger_callback('on_loading', False, "")
            return False
    
    # ==================== Data Processing ====================
    
    def _process_weather_data(self, data: Dict, city: str) -> Dict:
        """
        Process Group 1's API data into GUI-friendly format
        
        Group 1's data format:
        {
            'weather_condition': 'Clear',
            'description': 'clear sky',
            'temperature': 20,  # Already in Celsius
            'pressure': 1013,
            'humidity': 65
        }
        
        Args:
            data: Parsed data from Group 1's API
            city: City name
            
        Returns:
            Dict: Processed data ready for GUI display
        """
        processed = {
            # Location info
            'city': city.title(),
            'country': '',  # Group 1's API doesn't provide country
            
            # Weather description
            'main': data.get('weather_condition', 'Unknown'),
            'description': data.get('description', '').title(),
            
            # Temperature (already in Celsius from Group 1)
            'temp_celsius': data.get('temperature', 0),
            'feels_like_celsius': data.get('temperature', 0),  # Not provided, use same temp
            
            # Other weather data
            'humidity': data.get('humidity', 0),
            'pressure': data.get('pressure', 0),
            'wind_speed': 0,  # Not provided by Group 1's API
            
            # Raw data
            'raw': data
        }
        
        return processed
    
    # ==================== Data Retrieval ====================
    
    def get_current_weather(self) -> Optional[Dict]:
        """
        Get currently stored weather data
        
        Returns:
            Optional[Dict]: Current weather data or None
        """
        return self.current_weather_data
    
    def get_current_city(self) -> Optional[str]:
        """
        Get currently displayed city
        
        Returns:
            Optional[str]: Current city name or None
        """
        return self.current_city
    
    # ==================== Temperature Unit Conversion ====================
    
    def convert_temperature(self, temp_celsius: float, to_unit: str) -> float:
        """
        Convert temperature to specified unit
        
        Args:
            temp_celsius: Temperature in Celsius
            to_unit: Target unit ('celsius' or 'fahrenheit')
            
        Returns:
            float: Converted temperature
        """
        if to_unit.lower() == 'fahrenheit':
            return (temp_celsius * 9/5) + 32
        return temp_celsius
    
    def format_temperature(self, temp_celsius: float, unit: str = 'celsius') -> str:
        """
        Format temperature with unit symbol
        
        Args:
            temp_celsius: Temperature in Celsius
            unit: Display unit ('celsius' or 'fahrenheit')
            
        Returns:
            str: Formatted temperature string
        """
        temp = self.convert_temperature(temp_celsius, unit)
        symbol = '°F' if unit.lower() == 'fahrenheit' else '°C'
        return f"{temp:.1f}{symbol}"
    
    # ==================== Validation ====================
    
    def validate_city_input(self, city: str) -> tuple:
        """
        Validate city name input
        
        Args:
            city: City name to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not city or not city.strip():
            return False, "City name cannot be empty"
        
        if len(city.strip()) < 2:
            return False, "City name is too short"
        
        if len(city.strip()) > 100:
            return False, "City name is too long"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'äöüÄÖÜß")
        if not all(c in valid_chars for c in city):
            return False, "City name contains invalid characters"
        
        return True, ""
    
    # ==================== Refresh Data ====================
    
    def refresh_current_weather(self) -> bool:
        """
        Refresh weather data for currently displayed city
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.current_city:
            return self.fetch_weather(self.current_city)
        else:
            self._trigger_callback('on_error', 
                            "No City Selected", 
                            "Please search for a city first")
            return False


# ==================== Test Code ====================

if __name__ == "__main__":
    """Test the controller independently"""
    
    print("=" * 60)
    print("Testing Weather Controller")
    print("=" * 60)
    
    # Create controller
    controller = WeatherController()
    
    # Define test callback functions
    def on_success(data):
        print(f"\n✅ SUCCESS CALLBACK")
        print(f"   City: {data['city']}")
        print(f"   Temperature: {data['temp_celsius']:.1f}°C")
        print(f"   Condition: {data['description']}")
        print(f"   Humidity: {data['humidity']}%")
        print(f"   Pressure: {data['pressure']} hPa")
    
    def on_error(title, message):
        print(f"\n❌ ERROR CALLBACK")
        print(f"   {title}: {message}")
    
    def on_loading(is_loading, message):
        if is_loading:
            print(f"\n⏳ LOADING: {message}")
    
    # Register callbacks
    controller.register_callback('on_success', on_success)
    controller.register_callback('on_error', on_error)
    controller.register_callback('on_loading', on_loading)
    
    # Test fetching weather
    print("\n" + "=" * 60)
    print("Test 1: Fetch weather for London")
    print("=" * 60)
    controller.fetch_weather("London")
    
    print("\n" + "=" * 60)
    print("Test 2: Fetch weather for Berlin")
    print("=" * 60)
    controller.fetch_weather("Berlin")
    
    print("\n" + "=" * 60)
    print("Test 3: Invalid city (empty)")
    print("=" * 60)
    controller.fetch_weather("")
    
    print("\n" + "=" * 60)
    print("Test 4: Temperature conversion")
    print("=" * 60)
    print(f"20°C in Fahrenheit: {controller.format_temperature(20, 'fahrenheit')}")
    print(f"20°C in Celsius: {controller.format_temperature(20, 'celsius')}")
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)