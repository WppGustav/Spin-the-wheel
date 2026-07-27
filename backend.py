"""
backend.py
----------
All logic and data processing for the EVERS KÖK & BAR spin-the-wheel lottery.
The Streamlit frontend (app.py) should only call functions from this file
and never touch the data file or business rules directly.
"""

import json
import os
import random
import re
import time
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_FILE = "spins_data.json"          # simple local "database"
COOLDOWN_SECONDS = 1 * 60               # 1 minute between attempts after a loss
WIN_PROBABILITY = 0.50                  # 50% chance to win a free drink
BAR_NAME = "EVERS KÖK & BAR"
BAR_ADDRESS = "Stenkilsvägen 23, Vätö"
MIN_AGE = 18


# ---------------------------------------------------------------------------
# Data storage helpers
# ---------------------------------------------------------------------------

def _load_data() -> dict:
    """Load the attempts log. Keyed by phone number."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def validate_inputs(name: str, age, phone: str) -> list[str]:
    """Returns a list of human-readable error messages. Empty list = valid."""
    errors = []

    if not name or not name.strip():
        errors.append("Please enter your name.")

    if age is None or age == "":
        errors.append("Please enter your age.")
    else:
        try:
            age_int = int(age)
            if age_int < MIN_AGE:
                errors.append(f"You must be at least {MIN_AGE} years old to spin the wheel.")
            if age_int > 120:
                errors.append("Please enter a valid age.")
        except (ValueError, TypeError):
            errors.append("Age must be a whole number.")

    phone_clean = re.sub(r"[\s\-()]", "", phone or "")
    if not phone_clean:
        errors.append("Please enter your phone number.")
    elif not re.match(r"^\+?\d{6,15}$", phone_clean):
        errors.append("Please enter a valid phone number (digits only, 6-15 characters).")

    return errors


# ---------------------------------------------------------------------------
# Cooldown / spin eligibility
# ---------------------------------------------------------------------------

def can_spin(phone: str) -> tuple[bool, int]:
    """
    Checks whether this phone number is allowed to spin right now.
    Returns (allowed: bool, seconds_remaining: int).
    Only a LOSS triggers a cooldown; a win has no cooldown.
    """
    data = _load_data()
    phone_key = re.sub(r"[\s\-()]", "", phone or "")
    record = data.get(phone_key)

    if not record:
        return True, 0

    if record.get("result") == "lose":
        elapsed = time.time() - record.get("timestamp", 0)
        remaining = COOLDOWN_SECONDS - elapsed
        if remaining > 0:
            return False, int(remaining) + 1

    return True, 0


def determine_result() -> str:
    """Randomly decides the outcome based on WIN_PROBABILITY."""
    return "win" if random.random() < WIN_PROBABILITY else "lose"


def record_spin(name: str, age, phone: str, result: str) -> None:
    """Persists the outcome of a spin so cooldowns can be enforced."""
    data = _load_data()
    phone_key = re.sub(r"[\s\-()]", "", phone or "")
    data[phone_key] = {
        "name": name.strip(),
        "age": age,
        "result": result,
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat(timespec="seconds"),
    }
    _save_data(data)


# ---------------------------------------------------------------------------
# Certificate generation (for winners)
# ---------------------------------------------------------------------------

def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Tries to load a nice font, falls back to Pillow's default font."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default(size=size)


def generate_certificate(name: str) -> bytes:
    """
    Creates a simple red & white certificate JPEG for a winner and
    returns the raw JPEG bytes (ready for st.download_button).
    """
    width, height = 1200, 800
    red = (193, 18, 31)
    white = (255, 255, 255)

    img = Image.new("RGB", (width, height), white)
    draw = ImageDraw.Draw(img)

    # Border
    border = 18
    draw.rectangle([border, border, width - border, height - border], outline=red, width=8)
    draw.rectangle([border + 20, border + 20, width - border - 20, height - border - 20],
                    outline=red, width=2)

    title_font = _load_font(54, bold=True)
    subtitle_font = _load_font(28)
    name_font = _load_font(46, bold=True)
    body_font = _load_font(26)
    small_font = _load_font(20)

    def centered_text(y, text, font, fill=red):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((width - w) / 2, y), text, font=font, fill=fill)

    centered_text(90, BAR_NAME, title_font)
    centered_text(165, "Certificate of Winning", subtitle_font, fill=(80, 80, 80))

    draw.line([(150, 230), (width - 150, 230)], fill=red, width=3)

    centered_text(300, "This certifies that", body_font, fill=(80, 80, 80))
    centered_text(345, name.strip() if name.strip() else "Guest", name_font)
    centered_text(430, "has won a FREE DRINK 🍹", body_font, fill=red)
    centered_text(470, f"at {BAR_NAME}", body_font, fill=(80, 80, 80))
    centered_text(505, BAR_ADDRESS, body_font, fill=(80, 80, 80))

    draw.line([(150, 580), (width - 150, 580)], fill=red, width=3)

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    centered_text(620, f"Issued on {date_str}", small_font, fill=(120, 120, 120))
    centered_text(660, "Valid for one (1) free drink. Present this certificate at the bar.",
                  small_font, fill=(120, 120, 120))

    buffer = BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()
