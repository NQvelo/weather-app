"""
Icon loader utility for loading and caching Lucide icons as PNG images.
"""
import tkinter as tk
from pathlib import Path
from functools import lru_cache

# Path to icons directory
ICONS_DIR = Path(__file__).parent.parent.parent / 'icons'

# Cache for loaded images
_image_cache = {}

def load_icon(icon_name, size=None):
    """
    Load an icon as a PhotoImage.
    
    Args:
        icon_name (str): Name of the icon (without .png extension)
        size (tuple): Optional (width, height) to resize. If None, uses original size.
    
    Returns:
        tk.PhotoImage: The icon image, or None if not found
    """
    cache_key = (icon_name, size)
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    icon_path = ICONS_DIR / f"{icon_name}.png"
    
    if not icon_path.exists():
        # Fallback to default icon
        icon_path = ICONS_DIR / "default.png"
        if not icon_path.exists():
            return None
    
    try:
        image = tk.PhotoImage(file=str(icon_path))
        
        # Resize if requested using zoom/subsample
        if size:
            width, height = size
            orig_width = image.width()
            orig_height = image.height()
            
            # Calculate zoom factors
            if orig_width > 0 and orig_height > 0:
                zoom_x = width / orig_width
                zoom_y = height / orig_height
                
                # Use zoom for upscaling, subsample for downscaling
                if zoom_x >= 1.0 and zoom_y >= 1.0:
                    # Upscale
                    image = image.zoom(int(zoom_x), int(zoom_y))
                else:
                    # Downscale using subsample
                    subsample_x = max(1, int(orig_width / width))
                    subsample_y = max(1, int(orig_height / height))
                    image = image.subsample(subsample_x, subsample_y)
        
        # Cache the image (keep reference to prevent garbage collection)
        _image_cache[cache_key] = image
        return image
    except Exception as e:
        print(f"Error loading icon {icon_name} from {icon_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_icon_for_condition(condition, size=None):
    """
    Get the appropriate icon for a weather condition.
    
    Args:
        condition (str): Weather condition (e.g., 'clear', 'rain', 'clouds')
        size (tuple): Optional (width, height) to resize
    
    Returns:
        tk.PhotoImage: The icon image
    """
    condition_lower = condition.lower()
    
    # Map weather conditions to icon names
    if 'clear' in condition_lower or 'sunny' in condition_lower or 'sun' in condition_lower:
        icon_name = 'sun'
    elif 'rain' in condition_lower and 'drizzle' not in condition_lower:
        icon_name = 'rain'
    elif 'snow' in condition_lower:
        icon_name = 'snow'
    elif 'thunder' in condition_lower or 'lightning' in condition_lower:
        icon_name = 'thunderstorm'
    elif 'drizzle' in condition_lower:
        icon_name = 'drizzle'
    elif 'mist' in condition_lower or 'fog' in condition_lower or 'haze' in condition_lower:
        icon_name = 'fog'
    elif 'cloud' in condition_lower:
        icon_name = 'cloud'
    else:
        icon_name = 'default'
    
    return load_icon(icon_name, size)
