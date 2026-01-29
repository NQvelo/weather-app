"""
Main content area: current weather, details, hourly and 15-day forecast.
"""
from datetime import datetime
import tkinter as tk
from types import SimpleNamespace

from .widgets import (
    create_rounded_rect,
    create_rounded_button,
    create_hourly_card,
    create_daily_card,
)
from .icon_loader import load_icon
from .theme import DETAIL_ICONS


def build_main_content(parent, colors, *,
                       scroll_hourly_left, scroll_hourly_right,
                       scroll_daily_left, scroll_daily_right):
    """
    Build the main content area and return a namespace with widget references.

    Returns an object with: city_label, temp_label, description_label, detail_cards,
    hourly_canvas, hourly_cards, hourly_card_width, daily_canvas, daily_cards, daily_card_width.
    """
    main = tk.Frame(parent, bg=colors['bg_dark'])
    main.grid(row=0, column=1, sticky='nsew', padx=(0, 15), pady=(30, 15))
    main.columnconfigure(0, weight=1)
    main.rowconfigure(2, weight=1)  # hourly
    main.rowconfigure(3, weight=1)  # daily – same as hourly so both sections get equal height

    # --- Current weather ---
    current = tk.Frame(main, bg=colors['bg_dark'])
    current.grid(row=0, column=0, sticky='ew', pady=(0, 20))

    city_label = tk.Label(
        current, text="Loading", font=('Arial', 22, 'bold'),
        bg=colors['bg_dark'], fg=colors['text_primary']
    )
    city_label.pack(pady=(0, 10))

    temp_label = tk.Label(
        current, text="Loading", font=('Arial', 48, 'bold'),
        bg=colors['bg_dark'], fg=colors['text_primary']
    )
    temp_label.pack()

    description_label = tk.Label(
        current, text="Loading", font=('Arial', 20),
        bg=colors['bg_dark'], fg=colors['text_secondary']
    )
    description_label.pack()

    # --- Weather details (sunrise, sunset, etc.) ---
    details_frame = tk.Frame(main, bg=colors['bg_dark'])
    details_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))

    detail_cards = []
    for title, icon_name, default_value in [
        ("Sunrise", "sunrise", "Loading"),
        ("Sunset", "sunset", "Loading"),
        ("Visibility", "visibility", "Loading"),
        ("UV Index", "uv", "Loading"),
    ]:
        card = tk.Frame(details_frame, bg=colors['card_bg'])
        card.pack(side='left', fill='both', expand=True, padx=5)

        header = tk.Frame(card, bg=colors['card_bg'])
        header.pack(fill='x', pady=(15, 5))
        
        # Load icon as PhotoImage
        icon_img = load_icon(icon_name, size=(20, 20))
        icon_label = tk.Label(header, bg=colors['card_bg'])
        if icon_img:
            icon_label.config(image=icon_img)
            icon_label.image = icon_img  # Keep reference
        icon_label.pack(side='left', padx=(15, 5))
        
        title_label = tk.Label(header, text=title, font=('Arial', 10), bg=colors['card_bg'], fg=colors['text_secondary'])
        title_label.pack(side='left')

        value_label = tk.Label(
            card, text=default_value, font=('Arial', 12, 'bold'),
            bg=colors['card_bg'], fg=colors['text_primary']
        )
        value_label.pack(pady=(2, 15), padx=15, anchor='w')
        card.value_label = value_label
        detail_cards.append(card)

    # --- Hourly forecast ---
    hourly_card_width = 96
    hourly_canvas, hourly_cards = _build_forecast_strip(
        main, colors, row=2, title="Hourly Forecast",
        scroll_left=scroll_hourly_left, scroll_right=scroll_hourly_right,
        card_width=hourly_card_width,
        card_builder=lambda f, i: create_hourly_card(
            f, f"{(datetime.now().hour + i) % 24:02d}:00", "default", "--°", colors
        ),
        num_cards=24,
    )

    # --- 15-day forecast (same strip layout as hourly) ---
    daily_card_width = 96
    daily_canvas, daily_cards = _build_forecast_strip(
        main, colors, row=3, title="15 Day Forecast",
        pady=(15, 0),
        scroll_left=scroll_daily_left, scroll_right=scroll_daily_right,
        card_width=daily_card_width,
        card_builder=lambda f, i: create_daily_card(f, "---", "default", "--°/--°", colors),
        num_cards=15,
    )

    return SimpleNamespace(
        city_label=city_label,
        temp_label=temp_label,
        description_label=description_label,
        detail_cards=detail_cards,
        hourly_canvas=hourly_canvas,
        hourly_cards=hourly_cards,
        hourly_card_width=hourly_card_width,
        daily_canvas=daily_canvas,
        daily_cards=daily_cards,
        daily_card_width=daily_card_width,
    )


def _build_forecast_strip(parent, colors, *, row, title, scroll_left, scroll_right,
                          card_width, card_builder, num_cards, pady=(0, 0)):
    """Build a forecast strip (hourly or daily) with canvas, cards, and nav buttons."""
    forecast_canvas = tk.Canvas(parent, bg=colors['bg_dark'], highlightthickness=0)
    forecast_canvas.grid(row=row, column=0, sticky='nsew', pady=pady)

    forecast_container = tk.Frame(forecast_canvas, bg=colors['bg_dark'])

    def draw_bg(event=None):
        forecast_canvas.delete("forecast_bg")
        w, h = forecast_canvas.winfo_width(), forecast_canvas.winfo_height()
        if w > 1 and h > 1:
            create_rounded_rect(forecast_canvas, 0, 0, w, h, 10, fill=colors['bg_medium'], outline=colors['bg_medium'])

    forecast_canvas.bind('<Configure>', draw_bg)
    forecast_window = forecast_canvas.create_window(0, 0, window=forecast_container, anchor='nw')

    def update_size(event=None):
        w, h = forecast_canvas.winfo_width(), forecast_canvas.winfo_height()
        if w > 1 and h > 1:
            forecast_container.configure(width=w, height=h)
            forecast_canvas.itemconfig(forecast_window, width=w, height=h)
            draw_bg()

    forecast_canvas.bind('<Configure>', update_size)
    forecast_container.bind('<Configure>', lambda e: forecast_canvas.configure(scrollregion=forecast_canvas.bbox("all")))

    # Title and nav
    title_frame = tk.Frame(forecast_container, bg=colors['bg_dark'])
    title_frame.pack(fill='x', pady=(0, 15))
    tk.Label(title_frame, text=title, font=('Arial', 18, 'bold'), bg=colors['bg_dark'], fg=colors['text_primary'], anchor='w').pack(side='left')

    nav_frame = tk.Frame(title_frame, bg=colors['bg_dark'])
    nav_frame.pack(side='right')
    left_btn = create_rounded_button(nav_frame, "◀", scroll_left, colors)
    left_btn.pack(side='left', padx=3)
    right_btn = create_rounded_button(nav_frame, "▶", scroll_right, colors)
    right_btn.pack(side='left', padx=3)

    # Scrollable canvas for cards (pady 0,15 to match bottom padding between sections)
    strip_canvas = tk.Canvas(forecast_container, bg=colors['bg_medium'], highlightthickness=0, height=240)
    strip_canvas.pack(fill='x', expand=False, pady=(0, 15))

    strip_frame = tk.Frame(strip_canvas, bg=colors['bg_medium'])
    strip_canvas.create_window((0, 0), window=strip_frame, anchor='nw')

    def update_scroll(event=None):
        strip_canvas.configure(scrollregion=strip_canvas.bbox("all"))

    strip_frame.bind("<Configure>", update_scroll)

    def scroll_x(event):
        strip_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    strip_canvas.bind("<Enter>", lambda e: strip_canvas.bind_all("<MouseWheel>", scroll_x))
    strip_canvas.bind("<Leave>", lambda e: strip_canvas.unbind_all("<MouseWheel>"))

    cards = []
    for i in range(num_cards):
        card = card_builder(strip_frame, i)
        card.pack(side='left', padx=6, pady=5)
        cards.append(card)

    update_scroll()
    return strip_canvas, cards
