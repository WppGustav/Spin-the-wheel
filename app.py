"""
app.py
------
Frontend / UI only. All business logic lives in backend.py.

Run locally with:  streamlit run app.py
"""

import math
import random
import time

import streamlit as st
import streamlit.components.v1 as components

import backend

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EVERS KÖK & BAR – Spin the Wheel",
    page_icon="🍹",
    layout="centered",
)

RED = "#c1121f"
DARK_RED = "#780000"
WHITE = "#ffffff"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {WHITE};
        }}
        .header-banner {{
            background-color: {RED};
            color: {WHITE};
            padding: 1.6rem 1rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 1.2rem;
        }}
        .header-banner h1 {{
            margin: 0;
            font-size: 2.1rem;
            letter-spacing: 1px;
        }}
        .header-banner p {{
            margin: 0.3rem 0 0 0;
            font-size: 1rem;
            opacity: 0.9;
        }}
        div.stButton > button {{
            background-color: {RED};
            color: {WHITE};
            font-weight: 700;
            font-size: 1.1rem;
            padding: 0.7rem 0;
            border-radius: 10px;
            border: none;
            width: 100%;
        }}
        div.stButton > button:hover {{
            background-color: {DARK_RED};
            color: {WHITE};
        }}
        .rules-box {{
            border: 2px solid {RED};
            border-radius: 10px;
            padding: 1rem 1.2rem;
            background-color: #fff5f5;
            margin-bottom: 1rem;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="header-banner">
        <h1>🍹 EVERS KÖK &amp; BAR 🍹</h1>
        <p>Spin the Wheel — Win a Free Drink!</p>
        <p style="font-size:0.85rem;">Stenkilsvägen 23, Vätö</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="rules-box">
    <b>How it works:</b> Enter your details below and spin the wheel for a chance
    to win a free drink at the bar. If you lose, you can try again in 1 minute.
    If you win, you'll get a downloadable certificate to show at the bar.
    Must be 18 or older to participate.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Wheel drawing helpers
# ---------------------------------------------------------------------------

SEGMENTS = [
    {"label": "WIN 🍹", "color": RED, "text_color": WHITE, "win": True},
    {"label": "LOSE", "color": WHITE, "text_color": RED, "win": False},
    {"label": "WIN 🍹", "color": RED, "text_color": WHITE, "win": True},
    {"label": "LOSE", "color": WHITE, "text_color": RED, "win": False},
    {"label": "WIN 🍹", "color": RED, "text_color": WHITE, "win": True},
    {"label": "LOSE", "color": WHITE, "text_color": RED, "win": False},
    {"label": "WIN 🍹", "color": RED, "text_color": WHITE, "win": True},
    {"label": "LOSE", "color": WHITE, "text_color": RED, "win": False},
]
N_SEGMENTS = len(SEGMENTS)
SEGMENT_ANGLE = 360 / N_SEGMENTS


def _polar_to_xy(cx, cy, r, angle_deg):
    angle_rad = math.radians(angle_deg - 90)  # 0 degrees = straight up
    return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)


def _build_wheel_svg() -> str:
    cx, cy, r = 150, 150, 145
    paths, labels = [], []
    for i, seg in enumerate(SEGMENTS):
        start_angle = i * SEGMENT_ANGLE
        end_angle = (i + 1) * SEGMENT_ANGLE
        x1, y1 = _polar_to_xy(cx, cy, r, start_angle)
        x2, y2 = _polar_to_xy(cx, cy, r, end_angle)
        path_d = f"M{cx},{cy} L{x1:.2f},{y1:.2f} A{r},{r} 0 0 1 {x2:.2f},{y2:.2f} Z"
        paths.append(f'<path d="{path_d}" fill="{seg["color"]}" stroke="{DARK_RED}" stroke-width="2"/>')

        mid_angle = start_angle + SEGMENT_ANGLE / 2
        lx, ly = _polar_to_xy(cx, cy, r * 0.62, mid_angle)
        labels.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" fill="{seg["text_color"]}" font-size="15" '
            f'font-weight="bold" text-anchor="middle" dominant-baseline="middle" '
            f'transform="rotate({mid_angle:.2f},{lx:.2f},{ly:.2f})">{seg["label"]}</text>'
        )

    return f"""
    <svg width="300" height="300" viewBox="0 0 300 300">
        {''.join(paths)}
        {''.join(labels)}
        <circle cx="{cx}" cy="{cy}" r="20" fill="{WHITE}" stroke="{RED}" stroke-width="5"/>
    </svg>
    """


def _compute_target_rotation(result: str, full_spins: int = 5) -> float:
    """Picks a rotation angle so the wheel visually lands on a segment matching `result`."""
    matching = [i for i, s in enumerate(SEGMENTS) if s["win"] == (result == "win")]
    idx = random.choice(matching)
    center = idx * SEGMENT_ANGLE + SEGMENT_ANGLE / 2
    target_mod = (360 - center) % 360
    return full_spins * 360 + target_mod


def _build_wheel_html(rotation_deg: float) -> str:
    svg = _build_wheel_svg()
    return f"""
    <div style="display:flex; flex-direction:column; align-items:center; font-family:sans-serif;">
      <div style="position:relative; width:300px; height:320px;">
        <div style="position:absolute; top:-5px; left:135px; width:0; height:0;
                    border-left:14px solid transparent; border-right:14px solid transparent;
                    border-top:24px solid {DARK_RED}; z-index:10;"></div>
        <div id="wheel" style="width:300px; height:300px; margin-top:20px;
                    transform: rotate(0deg);
                    transition: transform 4s cubic-bezier(0.15, 0.65, 0.25, 1);">
            {svg}
        </div>
      </div>
    </div>
    <script>
      setTimeout(function() {{
        var wheel = document.getElementById('wheel');
        if (wheel) {{ wheel.style.transform = 'rotate({rotation_deg}deg)'; }}
      }}, 150);
    </script>
    """


def _build_static_wheel_html() -> str:
    svg = _build_wheel_svg()
    return f"""
    <div style="display:flex; flex-direction:column; align-items:center; font-family:sans-serif;">
      <div style="position:relative; width:300px; height:320px;">
        <div style="position:absolute; top:-5px; left:135px; width:0; height:0;
                    border-left:14px solid transparent; border-right:14px solid transparent;
                    border-top:24px solid {DARK_RED}; z-index:10;"></div>
        <div style="width:300px; height:300px; margin-top:20px;">{svg}</div>
      </div>
    </div>
    """


# ---------------------------------------------------------------------------
# Result popup
# ---------------------------------------------------------------------------

@st.dialog("🎉 The wheel has spoken!")
def show_result_dialog(result: str, name: str):
    if result == "win":
        st.balloons()
        st.success(f"🎉 Congratulations, {name.strip() or 'friend'}! You WON a free drink!")
        st.write("Download your certificate and show it at the bar:")
        cert_bytes = backend.generate_certificate(name)
        st.image(cert_bytes, use_container_width=True)
        st.download_button(
            label="⬇️ Download your certificate (JPEG)",
            data=cert_bytes,
            file_name=f"evers_kok_bar_certificate_{name.strip().replace(' ', '_') or 'winner'}.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )
    else:
        st.error("😢 So close! You didn't win this time.")
        st.write("You can spin again in **1 minute** — good luck next time!")

    if st.button("Close", use_container_width=True):
        st.rerun()


# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------

st.subheader("Enter your details")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name", placeholder="Jane Doe")
with col2:
    age = st.number_input("Age", min_value=0, max_value=120, step=1, value=None, placeholder="18")

phone = st.text_input("Phone number", placeholder="07XXXXXXXX")

st.write("")

spin_clicked = st.button("🎰 SPIN THE WHEEL", use_container_width=True)

wheel_area = st.container()

if spin_clicked:
    errors = backend.validate_inputs(name, age, phone)
    if errors:
        for e in errors:
            st.error(e)
        with wheel_area:
            components.html(_build_static_wheel_html(), height=340)
    else:
        allowed, wait_seconds = backend.can_spin(phone)
        if not allowed:
            minutes, seconds = divmod(wait_seconds, 60)
            st.warning(
                f"⏳ You've already spun! Please wait **{minutes}m {seconds}s** "
                f"before trying again."
            )
            with wheel_area:
                components.html(_build_static_wheel_html(), height=340)
        else:
            result = backend.determine_result()
            backend.record_spin(name, age, phone, result)
            rotation = _compute_target_rotation(result)

            with wheel_area:
                with st.spinner("Spinning... good luck! 🍀"):
                    components.html(_build_wheel_html(rotation), height=340)
                    time.sleep(4.6)

            show_result_dialog(result, name)
else:
    with wheel_area:
        components.html(_build_static_wheel_html(), height=340)

st.write("")
st.caption(f"{backend.BAR_NAME} · {backend.BAR_ADDRESS} · Must be {backend.MIN_AGE}+ to participate.")
