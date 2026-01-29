"""
Reusable UI widgets and drawing helpers for the Weather App.
"""
import math
import tkinter as tk
from .icon_loader import load_icon, get_icon_for_condition


def create_rounded_rect(canvas, x1, y1, x2, y2, radius, fill, outline=""):
    """
    Draw a rounded rectangle on a canvas.

    Args:
        canvas: The canvas to draw on
        x1, y1: Top-left corner coordinates
        x2, y2: Bottom-right corner coordinates
        radius: Border radius in pixels
        fill: Fill color
        outline: Outline color (optional)
    """
    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = []
    segments = 12

    for i in range(segments + 1):
        angle = math.pi * (1.5 + i / segments * 0.5)
        px = x1 + radius + radius * math.cos(angle)
        py = y1 + radius + radius * math.sin(angle)
        points.append((px, py))

    for i in range(segments + 1):
        angle = math.pi * (1.0 - i / segments * 0.5)
        px = x2 - radius + radius * math.cos(angle)
        py = y1 + radius + radius * math.sin(angle)
        points.append((px, py))

    for i in range(segments + 1):
        angle = math.pi * (0.5 - i / segments * 0.5)
        px = x2 - radius + radius * math.cos(angle)
        py = y2 - radius + radius * math.sin(angle)
        points.append((px, py))

    for i in range(segments + 1):
        angle = math.pi * (0.0 - i / segments * 0.5)
        px = x1 + radius + radius * math.cos(angle)
        py = y2 - radius + radius * math.sin(angle)
        points.append((px, py))

    flat_points = [c for p in points for c in p]
    outline_color = outline or fill
    canvas.create_polygon(flat_points, fill=fill, outline=outline_color, smooth=True, width=0)


def create_rounded_button(parent, text, command, colors):
    """Create a small, fully rounded navigation button."""
    btn_canvas = tk.Canvas(
        parent, width=32, height=32,
        bg=colors['bg_dark'], highlightthickness=0,
        relief='flat', bd=0
    )

    def draw_button(fill_color):
        btn_canvas.delete("all")
        btn_canvas.create_oval(2, 2, 30, 30, fill=fill_color, outline=fill_color, width=0)
        btn_canvas.create_text(16, 16, text=text, font=('Arial', 11, 'bold'), fill=colors['text_primary'])

    draw_button(colors['card_bg'])

    def on_click(event):
        command()

    def on_enter(event):
        draw_button(colors['bg_medium'])

    def on_leave(event):
        draw_button(colors['card_bg'])

    btn_canvas.bind('<Button-1>', on_click)
    btn_canvas.bind('<Enter>', on_enter)
    btn_canvas.bind('<Leave>', on_leave)
    btn_canvas.config(cursor='hand2')
    return btn_canvas


def create_hourly_card(parent, time, icon, temp, colors):
    """
    Create a single hourly forecast card.
    
    Args:
        parent: Parent widget
        time: Time string (e.g., "14:00")
        icon: Icon name (str) or PhotoImage object
        temp: Temperature string (e.g., "20°C")
        colors: Color dictionary
    """
    card_canvas = tk.Canvas(
        parent, bg=colors['bg_medium'],
        highlightthickness=0, width=90, height=180
    )
    card_canvas.pack_propagate(False)

    create_rounded_rect(card_canvas, 0, 0, 90, 180, 10, fill=colors['card_bg'], outline=colors['card_bg'])

    content_canvas = tk.Canvas(
        card_canvas, bg=colors['card_bg'],
        highlightthickness=0, width=90, height=180
    )
    content_canvas.pack_propagate(False)
    create_rounded_rect(content_canvas, 0, 0, 90, 180, 10, fill=colors['card_bg'], outline=colors['card_bg'])

    card_canvas.create_window(0, 0, window=content_canvas, anchor='nw', width=90, height=180)

    card = tk.Frame(content_canvas, bg=colors['card_bg'], width=90, height=180)
    content_canvas.create_window(0, 0, window=card, anchor='nw', width=90, height=180)

    time_label = tk.Label(card, text=time, font=('Arial', 11), bg=colors['card_bg'], fg=colors['text_secondary'])
    time_label.pack(pady=(8, 3))
    
    # Handle icon - can be PhotoImage or icon name string
    icon_label = tk.Label(card, bg=colors['card_bg'])
    if isinstance(icon, tk.PhotoImage):
        icon_label.config(image=icon)
        icon_label.image = icon  # Keep reference
    elif isinstance(icon, str):
        # Try to load icon by name first, then by condition
        icon_img = load_icon(icon, size=(32, 32)) or get_icon_for_condition(icon, size=(32, 32)) or load_icon('default', size=(32, 32))
        if icon_img:
            icon_label.config(image=icon_img)
            icon_label.image = icon_img  # Keep reference
    icon_label.pack(pady=4)
    
    temp_label = tk.Label(card, text=temp, font=('Arial', 18, 'bold'), bg=colors['card_bg'], fg=colors['text_primary'])
    temp_label.pack(pady=(3, 8))

    card_canvas.temp_label = temp_label
    card_canvas.icon_label = icon_label
    card_canvas.time_label = time_label
    card_canvas.card_frame = card
    return card_canvas


def create_daily_card(parent, day, icon, temp_str, colors):
    """
    Create a daily forecast card (same layout as hourly).
    
    Args:
        parent: Parent widget
        day: Day string (e.g., "Mon 27")
        icon: Icon name (str) or PhotoImage object
        temp_str: Temperature string (e.g., "20°/15°")
        colors: Color dictionary
    """
    card_canvas = tk.Canvas(
        parent, bg=colors['bg_medium'],
        highlightthickness=0, width=90, height=180
    )
    card_canvas.pack_propagate(False)

    create_rounded_rect(card_canvas, 0, 0, 90, 180, 10, fill=colors['card_bg'], outline=colors['card_bg'])

    content_canvas = tk.Canvas(
        card_canvas, bg=colors['card_bg'],
        highlightthickness=0, width=90, height=180
    )
    content_canvas.pack_propagate(False)
    create_rounded_rect(content_canvas, 0, 0, 90, 180, 10, fill=colors['card_bg'], outline=colors['card_bg'])

    card_canvas.create_window(0, 0, window=content_canvas, anchor='nw', width=90, height=180)

    card = tk.Frame(content_canvas, bg=colors['card_bg'], width=90, height=180)
    content_canvas.create_window(0, 0, window=card, anchor='nw', width=90, height=180)

    day_label = tk.Label(card, text=day, font=('Arial', 11), bg=colors['card_bg'], fg=colors['text_secondary'])
    day_label.pack(pady=(8, 3))
    
    # Handle icon - can be PhotoImage or icon name string
    icon_label = tk.Label(card, bg=colors['card_bg'])
    if isinstance(icon, tk.PhotoImage):
        icon_label.config(image=icon)
        icon_label.image = icon  # Keep reference
    elif isinstance(icon, str):
        # Try to load icon by name first, then by condition
        icon_img = load_icon(icon, size=(32, 32)) or get_icon_for_condition(icon, size=(32, 32)) or load_icon('default', size=(32, 32))
        if icon_img:
            icon_label.config(image=icon_img)
            icon_label.image = icon_img  # Keep reference
    icon_label.pack(pady=4)
    
    temp_label = tk.Label(card, text=temp_str, font=('Arial', 18, 'bold'), bg=colors['card_bg'], fg=colors['text_primary'])
    temp_label.pack(pady=(3, 8))

    card_canvas.day_label = day_label
    card_canvas.icon_label = icon_label
    card_canvas.temp_label = temp_label
    card_canvas.card_frame = card
    return card_canvas
