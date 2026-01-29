"""
Load weather and detail icons from assets/icons SVG files and expose them as
Tkinter PhotoImages. Uses svglib + ReportLab to render SVG to PIL, then ImageTk.
"""
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageTk
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

# Base path to assets/icons (project root / assets / icons)
_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "icons"

# Map all icon names used in app (weather_api, theme, widgets) -> SVG basename (no .svg)
WEATHER_ICON_TO_SVG = {
    "sun": "sun",
    "cloud": "cloud",
    "cloudrain": "cloud-rain",
    "cloudRain": "cloud-rain",
    "cloud-rain": "cloud-rain",
    "clouddrizzle": "cloud-drizzle",
    "cloudDrizzle": "cloud-drizzle",
    "cloud-drizzle": "cloud-drizzle",
    "drizzle": "cloud-drizzle",
    "zap": "cloud-lightning",
    "cloud-lightning": "cloud-lightning",
    "thunderstorm": "cloud-lightning",
    "snowflake": "snowflake",
    "snow": "snowflake",
    "cloudfog": "cloud-fog",
    "cloudFog": "cloud-fog",
    "cloud-fog": "cloud-fog",
    "fog": "cloud-fog",
    "mist": "cloud-fog",
    "haze": "cloud-fog",
    "moon": "moon",
}

# Detail icons (sunrise, sunset, visibility, uv)
DETAIL_ICON_TO_SVG = {
    "sunrise": "sunrise",
    "sunset": "sunset",
    "visibility": "eye",
    "uv": "sun",
}

_CACHE = {}


def _render_svg_to_pil(svg_path: Path, color: str, size_px: int) -> Image.Image:
    """Load SVG, replace currentColor with color, render to PIL Image at size_px x size_px."""
    raw = svg_path.read_text(encoding="utf-8")
    # Replace currentColor so stroke/fill use our theme color
    colored = raw.replace("currentColor", color)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".svg", delete=False, encoding="utf-8"
    ) as f:
        f.write(colored)
        tmp_svg = f.name

    try:
        drawing = svg2rlg(tmp_svg)
        if drawing is None:
            raise ValueError(f"svglib could not parse {svg_path.name}")
        # Optional: scale drawing for sharper output at small sizes
        base = max(drawing.width, drawing.height, 24)
        if base > 0:
            scale = size_px / base
            drawing.scale(scale, scale)
            drawing.width = size_px
            drawing.height = size_px

        try:
            img = renderPM.drawToPIL(drawing)
        except AttributeError:
            tmp_png = tempfile.mktemp(suffix=".png")
            try:
                renderPM.drawToFile(drawing, tmp_png, fmt="PNG")
                img = Image.open(tmp_png).copy()
            finally:
                if os.path.exists(tmp_png):
                    os.unlink(tmp_png)

        if img.size[0] != size_px or img.size[1] != size_px:
            img = img.resize((size_px, size_px), Image.Resampling.LANCZOS)
        return img
    finally:
        if os.path.exists(tmp_svg):
            os.unlink(tmp_svg)


def _pil_to_photoimage(img: Image.Image):
    """Convert PIL Image to Tkinter PhotoImage. Flatten RGBA to RGB on dark bg."""
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, "#1e1e2e")
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return ImageTk.PhotoImage(image=img)


def get_weather_icon(name: str, size: int = 32, color: str = "#ffffff"):
    """
    Return a Tkinter PhotoImage for a weather icon.

    `name` can be any of: sun, cloud, cloudRain, cloud-drizzle, zap, snowflake,
    cloudFog, fog, moon, etc. Mapped to assets/icons/*.svg.
    """
    key = ("weather", str(name).lower(), size, color)
    if key in _CACHE:
        return _CACHE[key]

    base = WEATHER_ICON_TO_SVG.get(str(name).lower()) or WEATHER_ICON_TO_SVG.get(
        str(name).replace("-", "")
    )
    if not base:
        base = "cloud"
    svg_path = _ASSETS_DIR / f"{base}.svg"
    if not svg_path.exists():
        svg_path = _ASSETS_DIR / "cloud.svg"

    img = _render_svg_to_pil(svg_path, color, size)
    photo = _pil_to_photoimage(img)
    _CACHE[key] = photo
    return photo


def get_detail_icon(icon_type: str, size: int = 20, color: str = "#ffffff"):
    """
    Return a Tkinter PhotoImage for a detail icon (sunrise, sunset, visibility, uv).
    """
    key = ("detail", str(icon_type).lower(), size, color)
    if key in _CACHE:
        return _CACHE[key]

    base = DETAIL_ICON_TO_SVG.get(str(icon_type).lower(), "sun")
    svg_path = _ASSETS_DIR / f"{base}.svg"
    if not svg_path.exists():
        svg_path = _ASSETS_DIR / "sun.svg"

    img = _render_svg_to_pil(svg_path, color, size)
    photo = _pil_to_photoimage(img)
    _CACHE[key] = photo
    return photo
