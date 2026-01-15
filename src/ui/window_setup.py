
import sys
import os
from pathlib import Path
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from src.ui.weather_controller import WeatherController

current_dir = Path(__file__).parent
src_dir = current_dir.parent
project_root = src_dir.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.controller = WeatherController()
        
        self.controller.register_callback('on_success', self.on_weather_success)
        self.controller.register_callback('on_error', self.on_weather_error)
        self.controller.register_callback('on_loading', self.on_loading)
        
        self.german_cities = ["Zweibrücken", "Zwickau", "Berlin", "Munich", "Hamburg", "Frankfurt", 
                            "Cologne", "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig", 
                            "Bremen", "Dresden", "Hanover", "Nuremberg", "Duisburg"]
        
        self.weather_icons = {
            'clear': '☀️', 'sunny': '☀️', 'clouds': '☁️', 'cloudy': '☁️',
            'rain': '🌧️', 'rainy': '🌧️', 'snow': '❄️', 'snowy': '❄️',
            'thunderstorm': '⛈️', 'drizzle': '🌦️', 'mist': '🌫️', 'fog': '🌫️', 
            'haze': '🌫️', 'default': '🌤️'
        }
        
        self.setup_window()
        self.create_widgets()
        self.load_weather_for_city("Zwickau")
    
    def setup_window(self):
        self.root.title("Weather Forecast App")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        self.colors = {
            'bg_dark': '#1e1e2e',
            'bg_medium': '#2d2d44',
            'bg_light': '#3d3d5c',
            'sidebar_bg': '#252538',
            'accent': '#6366f1',
            'text_primary': '#ffffff',
            'text_secondary': '#b4b4c8',
            'card_bg': '#2d2d44'
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 700
        y = (self.root.winfo_screenheight() // 2) - 400
        self.root.geometry(f'1400x800+{x}+{y}')
    
    def create_widgets(self):
        self.create_sidebar()
        self.create_main_content()
    
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.colors['sidebar_bg'], width=200)
        sidebar.grid(row=0, column=0, sticky='nsew', padx=15, pady=15)
        sidebar.grid_propagate(False)
        
        search_frame = tk.Frame(sidebar, bg=self.colors['sidebar_bg'])
        search_frame.pack(fill='x', padx=10, pady=(10, 20))
        
        self.sidebar_search = tk.Entry(
            search_frame, font=('Arial', 11), bg=self.colors['bg_light'],
            fg=self.colors['text_primary'], insertbackground='white', relief='flat', bd=0
        )
        self.sidebar_search.pack(fill='x', ipady=8, padx=5)
        self.sidebar_search.insert(0, "  🔍 Search city...")
        self.sidebar_search.bind('<Return>', lambda e: self.search_city())
        self.sidebar_search.bind('<FocusIn>', self.on_search_focus_in)
        self.sidebar_search.bind('<FocusOut>', self.on_search_focus_out)
        
        list_frame = tk.Frame(sidebar, bg=self.colors['sidebar_bg'])
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.city_buttons = []
        for city in self.german_cities:
            btn_frame = tk.Frame(list_frame, bg=self.colors['bg_light'], bd=0)
            btn_frame.pack(fill='x', pady=3)
            
            btn = tk.Button(
                btn_frame, text=city, font=('Arial', 11), bg=self.colors['bg_light'],
                fg=self.colors['text_primary'], activebackground=self.colors['accent'],
                activeforeground='white', relief='flat', anchor='w', padx=15, pady=10,
                cursor='hand2', command=lambda c=city: self.load_weather_for_city(c)
            )
            btn.pack(fill='both')
            
            temp_label = tk.Label(
                btn_frame, text="--°", font=('Arial', 10),
                bg=self.colors['bg_light'], fg=self.colors['text_secondary']
            )
            temp_label.place(relx=0.85, rely=0.5, anchor='center')
            self.city_buttons.append((btn_frame, btn, temp_label, city))
    
    def create_main_content(self):
        main = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main.grid(row=0, column=1, sticky='nsew', padx=(0, 15), pady=15)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)
        
        # Current Weather
        self.create_current_weather(main)
        
        # Weather Details (4 cards)
        self.create_weather_details(main)
        
        # Hourly Forecast
        self.create_hourly_forecast(main)
    
    def create_current_weather(self, parent):
        current = tk.Frame(parent, bg=self.colors['bg_dark'])
        current.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        self.city_label = tk.Label(
            current, text="Loading...", font=('Arial', 36, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text_primary']
        )
        self.city_label.pack()
        
        self.temp_label = tk.Label(
            current, text="--°C", font=('Arial', 80, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text_primary']
        )
        self.temp_label.pack()
        
        self.description_label = tk.Label(
            current, text="Fetching weather...", font=('Arial', 20),
            bg=self.colors['bg_dark'], fg=self.colors['text_secondary']
        )
        self.description_label.pack()
    
    def create_weather_details(self, parent):
        details_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        details_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        # Changed to match screenshot: Sunrise, Sunset, Visibility, UV Index
        self.detail_cards = []
        details_config = [
            ("Sunrise", "☀️", "--"),
            ("Sunset", "🌙", "--"),
            ("Visibility", "👁️", "--"),
            ("UV Index", "☀️", "--")
        ]
        
        for title, icon, default_value in details_config:
            card = tk.Frame(details_frame, bg=self.colors['card_bg'])
            card.pack(side='left', fill='both', expand=True, padx=5)
            
            header = tk.Frame(card, bg=self.colors['card_bg'])
            header.pack(fill='x', pady=(15, 5))
            
            icon_label = tk.Label(
                header, text=icon, font=('Arial', 20), bg=self.colors['card_bg']
            )
            icon_label.pack(side='left', padx=(15, 5))
            
            title_label = tk.Label(
                header, text=title, font=('Arial', 12),
                bg=self.colors['card_bg'], fg=self.colors['text_secondary']
            )
            title_label.pack(side='left')
            
            value_label = tk.Label(
                card, text=default_value, font=('Arial', 16, 'bold'),
                bg=self.colors['card_bg'], fg=self.colors['text_primary']
            )
            value_label.pack(pady=(0, 15), padx=15, anchor='w')
            
            card.value_label = value_label
            self.detail_cards.append(card)
    
    def create_hourly_forecast(self, parent):
        forecast_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        forecast_container.grid(row=2, column=0, sticky='nsew')
        
        title_label = tk.Label(
            forecast_container, text="Hourly Forecast", font=('Arial', 18, 'bold'),
            bg=self.colors['bg_dark'], fg=self.colors['text_primary'], anchor='w'
        )
        title_label.pack(fill='x', pady=(0, 15))
        
        # Scrollable canvas
        canvas = tk.Canvas(
            forecast_container, bg=self.colors['bg_medium'],
            highlightthickness=0, height=280
        )
        canvas.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(forecast_container, orient='horizontal', command=canvas.xview)
        scrollbar.pack(fill='x')
        canvas.configure(xscrollcommand=scrollbar.set)
        
        hourly_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        canvas.create_window((0, 0), window=hourly_frame, anchor='nw')
        
        # Create hourly cards
        self.hourly_cards = []
        current_hour = datetime.now().hour
        
        for i in range(14):
            hour = (current_hour + i) % 24
            card = self.create_hourly_card(hourly_frame, f"{hour:02d}:00", "🌤️", "--°")
            card.pack(side='left', padx=5, pady=10)
            self.hourly_cards.append(card)
        
        hourly_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
    
    def create_hourly_card(self, parent, time, icon, temp):
        card = tk.Frame(parent, bg=self.colors['card_bg'], width=90, height=200)
        card.pack_propagate(False)
        
        time_label = tk.Label(
            card, text=time, font=('Arial', 11),
            bg=self.colors['card_bg'], fg=self.colors['text_secondary']
        )
        time_label.pack(pady=(20, 10))
        
        icon_label = tk.Label(
            card, text=icon, font=('Arial', 32), bg=self.colors['card_bg']
        )
        icon_label.pack(pady=15)
        
        temp_label = tk.Label(
            card, text=temp, font=('Arial', 18, 'bold'),
            bg=self.colors['card_bg'], fg=self.colors['text_primary']
        )
        temp_label.pack(pady=(10, 20))
        
        card.temp_label = temp_label
        card.icon_label = icon_label
        card.time_label = time_label
        return card
    
    # API Integration Methods
    
    def load_weather_for_city(self, city):
        self.controller.fetch_weather(city)
    
    def search_city(self):
        term = self.sidebar_search.get().replace("  🔍 Search city...", "").strip()
        if term:
            self.load_weather_for_city(term)
    
    def on_weather_success(self, data):
        # Update main display
        self.city_label.config(text=data['city'])
        self.temp_label.config(text=f"{data['temp_celsius']:.0f}°C")
        
        icon = self.get_weather_icon(data['main'])
        self.description_label.config(text=f"{icon} {data['description']}")
        
        # Update detail cards with actual API data
        # Sunrise (placeholder - Group 1's API doesn't provide this)
        self.detail_cards[0].value_label.config(text="6:45 AM")
        
        # Sunset (placeholder)
        self.detail_cards[1].value_label.config(text="8:49 PM")
        
        # Visibility (placeholder)
        self.detail_cards[2].value_label.config(text="7 km")
        
        # UV Index (placeholder)
        self.detail_cards[3].value_label.config(text="Moderate")
        
        # Update hourly forecast with varying temperatures
        base_temp = data['temp_celsius']
        current_hour = datetime.now().hour
        
        for i, card in enumerate(self.hourly_cards):
            hour = (current_hour + i) % 24
            # Simulate temperature variation
            temp_variation = (i * 2) - 7  # Varies from -7 to +20
            hourly_temp = base_temp + temp_variation
            
            card.time_label.config(text=f"{hour:02d}:00")
            card.temp_label.config(text=f"{hourly_temp:.0f}°")
            
            # Vary icons based on time
            if 6 <= hour < 12:
                hourly_icon = "🌤️" if i % 2 == 0 else "☁️"
            elif 12 <= hour < 18:
                hourly_icon = "☀️" if i % 3 == 0 else "🌤️"
            else:
                hourly_icon = "🌙" if hour >= 20 else "🌤️"
            
            card.icon_label.config(text=hourly_icon)
        
        # Update sidebar temperatures
        for _, _, temp_label, btn_city in self.city_buttons:
            if btn_city.lower() == data['city'].lower():
                temp_label.config(text=f"{data['temp_celsius']:.0f}°")
                break
    
    def on_weather_error(self, title, message):
        messagebox.showerror(title, message)
    
    def on_loading(self, is_loading, message):
        if is_loading:
            self.root.config(cursor="wait")
            self.root.update()
        else:
            self.root.config(cursor="")
    
    def on_search_focus_in(self, event):
        if self.sidebar_search.get() == "  🔍 Search city...":
            self.sidebar_search.delete(0, tk.END)
    
    def on_search_focus_out(self, event):
        if not self.sidebar_search.get():
            self.sidebar_search.insert(0, "  🔍 Search city...")
    
    def get_weather_icon(self, condition):
        for key in self.weather_icons:
            if key in condition.lower():
                return self.weather_icons[key]
        return self.weather_icons['default']


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()