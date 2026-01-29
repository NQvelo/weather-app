"""
Main WeatherApp that composes sidebar, main content, and weather logic.
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from .theme import COLORS, WEATHER_ICONS, GERMAN_CITIES
from .weather_controller import WeatherController
from .sidebar import build_sidebar
from .main_content import build_main_content
from .icon_loader import get_icon_for_condition, load_icon


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.controller = WeatherController()
        self.temp_unit = 'celsius'
        self.current_weather_data = None
        self.colors = COLORS
        self.weather_icons = WEATHER_ICONS

        self.controller.register_callback('on_success', self.on_weather_success)
        self.controller.register_callback('on_error', self.on_weather_error)
        self.controller.register_callback('on_loading', self.on_loading)

        self.setup_window()
        self.create_widgets()
        self.update_unit_switcher_ui()
        self.load_weather_for_city("Zwickau")

    def setup_window(self):
        self.root.title("Weather Forecast App")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        self.root.configure(bg=self.colors['bg_dark'])
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 700
        y = (self.root.winfo_screenheight() // 2) - 400
        self.root.geometry(f'1400x800+{x}+{y}')

    def create_widgets(self):
        side = build_sidebar(
            self.root, self.colors, GERMAN_CITIES,
            on_city_click=self.load_weather_for_city,
            on_search=self.search_city,
            on_unit_change=self.set_temperature_unit,
            on_switcher_hover=self.on_switcher_hover,
            on_search_focus_in=self.on_search_focus_in,
            on_search_focus_out=self.on_search_focus_out,
        )
        self.sidebar_search = side.sidebar_search
        self.city_buttons = side.city_buttons
        self.unit_c_button = side.unit_c_button
        self.unit_f_button = side.unit_f_button

        main = build_main_content(
            self.root, self.colors,
            scroll_hourly_left=self.scroll_hourly_left,
            scroll_hourly_right=self.scroll_hourly_right,
            scroll_daily_left=self.scroll_daily_left,
            scroll_daily_right=self.scroll_daily_right,
        )
        self.city_label = main.city_label
        self.temp_label = main.temp_label
        self.description_label = main.description_label
        self.detail_cards = main.detail_cards
        self.hourly_canvas = main.hourly_canvas
        self.hourly_cards = main.hourly_cards
        self.hourly_card_width = main.hourly_card_width
        self.daily_canvas = main.daily_canvas
        self.daily_cards = main.daily_cards
        self.daily_card_width = main.daily_card_width

    # --- Actions ---

    def load_weather_for_city(self, city):
        self.controller.fetch_weather(city)

    def search_city(self):
        term = self.sidebar_search.get().replace("  🔍 Search city...", "").strip()
        if term:
            self.load_weather_for_city(term)

    def set_temperature_unit(self, unit):
        if unit == self.temp_unit:
            return
        self.temp_unit = unit
        self.update_unit_switcher_ui()
        if self.current_weather_data:
            self.update_temperature_displays(self.current_weather_data)

    def on_switcher_hover(self, unit, is_entering):
        if unit == 'c':
            button = self.unit_c_button
            is_active = self.temp_unit == 'celsius'
        else:
            button = self.unit_f_button
            is_active = self.temp_unit == 'fahrenheit'
        if is_entering and not is_active:
            button.config(bg=self.colors['bg_medium'])
        elif not is_entering and not is_active:
            button.config(bg=self.colors['bg_light'])

    def update_unit_switcher_ui(self):
        if self.temp_unit == 'celsius':
            self.unit_c_button.config(bg=self.colors['accent'], fg=self.colors['text_primary'])
            self.unit_f_button.config(bg=self.colors['bg_light'], fg=self.colors['text_secondary'])
        else:
            self.unit_c_button.config(bg=self.colors['bg_light'], fg=self.colors['text_secondary'])
            self.unit_f_button.config(bg=self.colors['accent'], fg=self.colors['text_primary'])

    # --- Weather controller callbacks ---

    def on_weather_success(self, data):
        self.current_weather_data = data
        self.city_label.config(text=data['city'])
        icon_img = self.get_weather_icon(data['main'], size=(32, 32))
        if icon_img:
            # Clear any existing text/image and set new image with text
            self.description_label.config(image=icon_img, text=f"  {data['description']}", compound='left')
            self.description_label.image = icon_img  # Keep reference
        else:
            self.description_label.config(image='', text=data['description'])

        self.detail_cards[0].value_label.config(text=data.get('sunrise', 'N/A'))
        self.detail_cards[1].value_label.config(text=data.get('sunset', 'N/A'))
        vis = data.get('visibility')
        self.detail_cards[2].value_label.config(text=f"{vis:.1f} km" if vis is not None else "N/A")
        self.detail_cards[3].value_label.config(text=data.get('uv_index', 'N/A'))
        self.update_temperature_displays(data)

    def on_weather_error(self, title, message):
        messagebox.showerror(title, message)

    def on_loading(self, is_loading, message):
        self.root.config(cursor="wait" if is_loading else "")
        if is_loading:
            self._show_loading_state()
            self.root.update()

    def _show_loading_state(self):
        """Show 'Loading' in all main content areas while fetching."""
        c = self.colors
        self.city_label.config(text="Loading")
        self.temp_label.config(text="Loading")
        self.description_label.config(image='', text="Loading")
        if hasattr(self.description_label, 'image'):
            self.description_label.image = None
        for card in self.detail_cards:
            card.value_label.config(text="Loading")
        for card in self.hourly_cards:
            card.time_label.config(text="Loading")
            card.temp_label.config(text="")
            card.icon_label.config(image='', text="Loading", fg=c['text_secondary'])
            if hasattr(card.icon_label, 'image'):
                card.icon_label.image = None
        for card in self.daily_cards:
            card.day_label.config(text="Loading")
            card.temp_label.config(text="")
            card.icon_label.config(image='', text="Loading", fg=c['text_secondary'])
            if hasattr(card.icon_label, 'image'):
                card.icon_label.image = None

    # --- Search ---

    def on_search_focus_in(self, event):
        if self.sidebar_search.get() == "  🔍 Search city...":
            self.sidebar_search.delete(0, tk.END)

    def on_search_focus_out(self, event):
        if not self.sidebar_search.get():
            self.sidebar_search.insert(0, "  🔍 Search city...")

    # --- Helpers ---

    def get_weather_icon(self, condition, size=(32, 32)):
        """
        Get PhotoImage icon for weather condition.
        
        Args:
            condition: Weather condition string
            size: Optional tuple (width, height) for icon size, defaults to (32, 32)
        
        Returns:
            tk.PhotoImage: The icon image
        """
        return get_icon_for_condition(condition, size=size) or load_icon('default', size=size)

    def update_temperature_displays(self, data):
        if self.temp_unit == 'fahrenheit':
            temp = self.controller.convert_temperature(data['temp_celsius'], 'fahrenheit')
            unit_symbol = '°F'
        else:
            temp = data['temp_celsius']
            unit_symbol = '°C'

        self.temp_label.config(text=f"{temp:.0f}{unit_symbol}")

        # Hourly
        hourly_forecast = data.get('hourly_forecast', [])
        if hourly_forecast:
            for i, card in enumerate(self.hourly_cards):
                if i < len(hourly_forecast):
                    item = hourly_forecast[i]
                    temp_c = item['temperature']
                    temp_display = self.controller.convert_temperature(temp_c, 'fahrenheit') if self.temp_unit == 'fahrenheit' else temp_c
                    card.time_label.config(text=item['time'])
                    card.temp_label.config(text=f"{temp_display:.0f}{unit_symbol}")
                    icon_img = self.get_weather_icon(item.get('condition', 'Unknown'), size=(32, 32))
                    if icon_img:
                        card.icon_label.config(image=icon_img, text='')
                        card.icon_label.image = icon_img  # Keep reference
                    else:
                        card.icon_label.config(image='', text='')
                else:
                    card.time_label.config(text="--:--")
                    card.temp_label.config(text=f"--{unit_symbol}")
                    default_icon = load_icon('default', size=(32, 32))
                    if default_icon:
                        card.icon_label.config(image=default_icon)
                        card.icon_label.image = default_icon
        else:
            base_temp = data['temp_celsius']
            current_hour = datetime.now().hour
            current_condition = data.get('main', 'Unknown')
            base_icon = self.get_weather_icon(current_condition, size=(32, 32))
            for i, card in enumerate(self.hourly_cards):
                hour = (current_hour + i) % 24
                temp_variation = ((i % 8) - 3.5) * 1.5
                hourly_temp_c = base_temp + temp_variation
                hourly_temp = self.controller.convert_temperature(hourly_temp_c, 'fahrenheit') if self.temp_unit == 'fahrenheit' else hourly_temp_c
                card.time_label.config(text=f"{hour:02d}:00")
                card.temp_label.config(text=f"{hourly_temp:.0f}{unit_symbol}")
                if hour >= 20 or hour < 6:
                    # Use moon icon for night, or base icon
                    if 'clear' in current_condition.lower() or 'sun' in current_condition.lower():
                        hourly_icon = load_icon('sunset', size=(32, 32)) or base_icon
                    else:
                        hourly_icon = base_icon
                else:
                    hourly_icon = base_icon
                if hourly_icon:
                    card.icon_label.config(image=hourly_icon, text='')
                    card.icon_label.image = hourly_icon
                else:
                    card.icon_label.config(image='', text='')

        # Daily
        daily_forecast = data.get('daily_forecast', [])
        if daily_forecast:
            for i, card in enumerate(self.daily_cards):
                if i < len(daily_forecast):
                    entry = daily_forecast[i]
                    t_high, t_low = entry.get('temperature_max'), entry.get('temperature_min')
                    if self.temp_unit == 'fahrenheit':
                        high = self.controller.convert_temperature(t_high, 'fahrenheit') if t_high is not None else None
                        low = self.controller.convert_temperature(t_low, 'fahrenheit') if t_low is not None else None
                    else:
                        high, low = t_high, t_low
                    temp_str = f"{high:.0f}°/ {low:.0f}°" if (high is not None and low is not None) else "--°/--°"
                    card.day_label.config(text=entry.get('day', '---'))
                    card.temp_label.config(text=temp_str)
                    icon_img = self.get_weather_icon(entry.get('condition', 'default'), size=(32, 32))
                    if icon_img:
                        card.icon_label.config(image=icon_img, text='')
                        card.icon_label.image = icon_img  # Keep reference
                    else:
                        card.icon_label.config(image='', text='')
                else:
                    card.day_label.config(text="---")
                    card.temp_label.config(text="--°/--°")
                    default_icon = load_icon('default', size=(32, 32))
                    if default_icon:
                        card.icon_label.config(image=default_icon, text='')
                        card.icon_label.image = default_icon
                    else:
                        card.icon_label.config(image='', text='')
        else:
            default_icon = load_icon('default', size=(32, 32))
            for card in self.daily_cards:
                card.day_label.config(text="---")
                card.temp_label.config(text="--°/--°")
                if default_icon:
                    card.icon_label.config(image=default_icon)
                    card.icon_label.image = default_icon
                else:
                    card.icon_label.config(image='', text='')

        # Sidebar city temps
        for _, _, temp_label, btn_city in self.city_buttons:
            if btn_city.lower() == data['city'].lower():
                temp_display = self.controller.convert_temperature(data['temp_celsius'], 'fahrenheit') if self.temp_unit == 'fahrenheit' else data['temp_celsius']
                temp_label.config(text=f"{temp_display:.0f}{unit_symbol}")
                break

    # --- Scroll ---

    def scroll_hourly_left(self):
        bbox = self.hourly_canvas.bbox("all")
        if bbox:
            content_width = bbox[2] - bbox[0]
            left, right = self.hourly_canvas.xview()
            scroll_fraction = self.hourly_card_width / content_width if content_width > 0 else 0.1
            self.hourly_canvas.xview_moveto(max(0.0, left - scroll_fraction))

    def scroll_hourly_right(self):
        bbox = self.hourly_canvas.bbox("all")
        if bbox:
            content_width = bbox[2] - bbox[0]
            left, right = self.hourly_canvas.xview()
            scroll_fraction = self.hourly_card_width / content_width if content_width > 0 else 0.1
            self.hourly_canvas.xview_moveto(min(1.0 - (right - left), left + scroll_fraction))

    def scroll_daily_left(self):
        bbox = self.daily_canvas.bbox("all")
        if bbox:
            content_width = bbox[2] - bbox[0]
            scroll_fraction = self.daily_card_width / content_width if content_width > 0 else 0.1
            left, right = self.daily_canvas.xview()
            self.daily_canvas.xview_moveto(max(0.0, left - scroll_fraction))

    def scroll_daily_right(self):
        bbox = self.daily_canvas.bbox("all")
        if bbox:
            content_width = bbox[2] - bbox[0]
            scroll_fraction = self.daily_card_width / content_width if content_width > 0 else 0.1
            left, right = self.daily_canvas.xview()
            self.daily_canvas.xview_moveto(min(1.0 - (right - left), left + scroll_fraction))
