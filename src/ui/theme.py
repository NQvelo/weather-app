"""
Theme and static configuration for the Weather App UI.
"""

# App color palette
COLORS = {
    'bg_dark': '#1e1e2e',
    'bg_medium': '#2d2d44',
    'bg_light': '#3d3d5c',
    'sidebar_bg': '#252538',
    'accent': '#6366f1',
    'text_primary': '#ffffff',
    'text_secondary': '#b4b4c8',
    'card_bg': '#2d2d44',
}

# Weather condition to icon file mapping (PNG icons)
WEATHER_ICONS = {
    'clear': 'sun', 'sunny': 'sun', 'clouds': 'cloud', 'cloudy': 'cloud',
    'rain': 'rain', 'rainy': 'rain', 'snow': 'snow', 'snowy': 'snow',
    'thunderstorm': 'thunderstorm', 'drizzle': 'drizzle', 'mist': 'fog', 'fog': 'fog',
    'haze': 'fog', 'default': 'cloud',
}

# Detail card icon mapping
DETAIL_ICONS = {
    'sunrise': 'sunrise',
    'sunset': 'sunset',
    'visibility': 'visibility',
    'uv': 'uv',
}

# Default list of German cities
GERMAN_CITIES = [
    "Zweibrücken", "Zwickau", "Berlin", "Munich", "Hamburg", "Frankfurt",
    "Cologne", "Stuttgart", "Düsseldorf",
]
