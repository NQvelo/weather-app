
import tkinter as tk
from src.ui.window_setup import WeatherApp
from src.ui.weather_controller import WeatherController

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
